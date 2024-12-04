import logging
from datetime import date, timedelta, datetime, time

import environs
import pytz
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from wbappointment.forms import AppointmentForm, SelectAppointmentDateForm
from wbappointment.models import Appointment, AppointmentStatus, ExpertSchedule, AppointmentPayment, \
    ExpertScheduleSpecialDays
from wbappointment.views.yookassa import create_yookassa_payment
from wbappointment.views.zoom_utils import create_zoom_meeting
from web.models import Expert
from web.services.timezone_translation import timezoneDictionary

env = environs.Env()
environs.Env.read_env()


info_logger = logging.getLogger("django-info")
debug_logger = logging.getLogger("django-debug")


def get_user_time_zone(request):
    if request.user.profile.timezone:
        target_timezone = request.user.profile.timezone
    else:
        target_timezone = 'Europe/Moscow'

    return pytz.timezone(target_timezone)



@login_required
def add_appointment_view(request, *args, **kwargs):
    expert = Expert.objects.get(pk=kwargs['pk'])

    if request.user == expert:
        return redirect("profile")



    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        # check for existing appointment for this date and time with this expert
        # don't create new one if already exist

        if form.is_valid():

            appointment_date = form.cleaned_data['appointment_date']
            appointment_time = form.cleaned_data['appointment_time']

            user_tz = get_user_time_zone(request)

            new_appointment_datetime = user_tz.localize(datetime.combine(appointment_date, appointment_time))

            existAppointment = Appointment.objects.filter(
                expert=expert,
                client=request.user,
                appointment_datetime=new_appointment_datetime,
                status=AppointmentStatus.NEW
            )

            if existAppointment.exists():
                # If already exist such appointent just work with it
                # No need to create new one
                form = AppointmentForm(request.POST, instance=existAppointment[0])


            new_appointment = form.save(commit=False)
            new_appointment.appointment_datetime = new_appointment_datetime
            new_appointment.client = request.user
            new_appointment.expert = expert

            # Получение текущего времени
            # end_time = form.cleaned_data['appointment_time'] + timedelta(hours=1)

            new_appointment.save()
            return redirect('appointment_checkout', pk=new_appointment.id)


    user_timezone = request.user.profile.timezone
    tz = pytz.timezone(user_timezone)

    # Получаем текущее время в указанном часовом поясе
    current_time = timezone.now().astimezone(tz)

    # Форматируем смещение
    offset = current_time.strftime('%z')
    offset_str = f"{offset[:3]}:{offset[3:]}"

    # Форматируем строку
    # formatted_timezone = f"{user_timezone} {offset_str}"
    formatted_timezone = f"{timezoneDictionary.get(str(tz), tz)} {offset_str}"

    form = AppointmentForm()
    not_avalable_dates = get_expert_working_dates(expert)
    context = {
        "formatted_timezone": formatted_timezone,
        "expert": expert,
        'form': form,
        'start_cal_date': not_avalable_dates['data']['start'],
        'end_cal_date': not_avalable_dates['data']['end'],
        'not_working_dates': not_avalable_dates['data']['not_working_dates']
    }

    return render(request, 'add_appointment.html', context=context)



def get_expert_working_dates(expert):
    calendar_period = 120  # days

    start_date = date.today()
    end_date = start_date + timedelta(days=calendar_period)

    # получаем номера дней из расписания когда эксперт работает
    expert_schedule_day_of_week = ExpertSchedule.objects.filter(expert=expert, is_work_day=True).values_list(
        'day_of_week', flat=True)
    expert_schedule_working_days_numbers = [value - 1 for value in expert_schedule_day_of_week]

    # expert_schedule_special_day_unavailable = ExpertScheduleSpecialDays.objects.filter(expert=expert, type=0, end__gte=datetime.now())
    expert_schedule_special_day_available = ExpertScheduleSpecialDays.objects.filter(expert=expert, type=1,
                                                                                     end__gte=datetime.now())

    extra_available_dates = []
    for extra_date in expert_schedule_special_day_available:
        current_date = extra_date.start.date()
        while current_date <= extra_date.end.date():
            if datetime.now().date() <= current_date:
                extra_available_dates.append(current_date)
            current_date += timedelta(days=1)

    not_working_dates = []

    for i in range(calendar_period + 1):
        day = start_date + timedelta(days=i)

        if day in extra_available_dates:
            continue

        if day.weekday() not in expert_schedule_working_days_numbers:
            not_working_dates.append(day.strftime("%Y-%m-%d"))

    return {'data': {"start": start_date.strftime("%Y-%m-%d"), "end": end_date.strftime("%Y-%m-%d"),
                     "not_working_dates": not_working_dates}}


@login_required()
def get_expert_available_timeslots(request):
    form = SelectAppointmentDateForm(request.GET)

    if form.is_valid():

        expert_id = form.cleaned_data['expert_id']
        selected_date = form.cleaned_data['selected_date']

        available_time_slots = []

        expert_schedule = ExpertSchedule.objects.filter(expert_id=expert_id, is_work_day=True,
                                                        day_of_week=selected_date.weekday() + 1).all()

        user_tz = get_user_time_zone(request)

        if len(expert_schedule) > 0:

            start_time = expert_schedule[0].start_datetime.astimezone(user_tz)
            end_time   = expert_schedule[0].end_datetime.astimezone(user_tz)

            current_date = datetime.now(user_tz)

            for hour in range(start_time.hour, end_time.hour):
                if current_date.date() == selected_date and hour <= current_date.hour:
                    continue
                available_time_slots.append(time(hour=hour, minute=0))

        expert_schedule_special_days = ExpertScheduleSpecialDays.objects.filter(start__date__gte=selected_date,
                                                                                end__date__lte=selected_date).all()



        for special_day in expert_schedule_special_days:
            current_date = special_day.start.astimezone(user_tz)
            while current_date <= special_day.end.astimezone(user_tz):
                if current_date.date() == selected_date:
                    if special_day.type == 0:
                        if current_date.time() in available_time_slots:
                            available_time_slots.remove(current_date.time())
                    if special_day.type == 1:
                        available_time_slots.append(current_date.time())
                else:
                    break

                current_date += timedelta(hours=1)

        # get busy expert's slot for certain date
        busyExpertsSlots = Appointment.objects.filter(expert_id=expert_id, appointment_datetime__date=selected_date)
                            #.annotate(appointment_time=TruncTime('appointment_datetime')).values_list("appointment_time", flat=True))

        for busy_datetime in busyExpertsSlots:
            busy_time = busy_datetime.appointment_datetime.astimezone(user_tz).time()
            if busy_time in available_time_slots:
                available_time_slots.remove(busy_time)

        busyClientsSlots = Appointment.objects.filter(client=request.user, appointment_datetime__date=selected_date)
                            #.annotate(appointment_time=TruncTime('appointment_datetime')).values_list("appointment_time", flat=True))

        for busy_datetime in busyClientsSlots:
            busy_time = busy_datetime.appointment_datetime.astimezone(user_tz).time()
            if busy_time in available_time_slots:
                available_time_slots.remove(busy_time)

        return JsonResponse([dt.strftime('%H:%M') for dt in available_time_slots], safe=False)

    return JsonResponse({'errors': dict(form.errors)}, status=400)


def appointment_test(request):
    appointment = Appointment.objects.get(pk=1)
    json_response = create_zoom_meeting(appointment)
    return JsonResponse({"zoom": json_response})


class AppointmentPaymentNotification(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payment_id = request.data['object']['id']
        debug_logger.debug("payment_id = " + payment_id)

        payment = AppointmentPayment.objects.get(uuid=payment_id)

        if payment.status == AppointmentPayment.AppointmentPaymentStatus.COMPLETED:
            debug_logger.debug("payment_id = " + payment_id + " already paid")
            return HttpResponse(status=200)

        debug_logger.debug("payment status is " + request.data['object']['status'])

        if request.data['object']['status'] == 'canceled':
            try:
                with transaction.atomic():
                    payment.status = AppointmentPayment.AppointmentPaymentStatus.CANCELED
                    payment.save()
                    payment.appointment.zoom_link = ''
                    payment.appointment.status = AppointmentStatus.CANCEL
                    payment.appointment.save()
            except Exception as e:
                # Если произошла ошибка, откатываем транзакцию
                debug_logger.debug(f"An error occurred: {e}")

        if request.data['object']['status'] == 'succeeded':
            try:
                with transaction.atomic():

                    zoom_link = create_zoom_meeting(payment.appointment)
                    payment.status = AppointmentPayment.AppointmentPaymentStatus.COMPLETED
                    payment.save()

                    payment.appointment.status = AppointmentStatus.PAID
                    payment.appointment.zoom_link = zoom_link
                    payment.appointment.save()

                    # Отправка уведомления Эксперту
                    html_content = render_to_string('emails/appointment_created.html',
                                                    {
                                                        'client': payment.appointment.client,
                                                        'appointment':payment.appointment,
                                                        'site_url': 'https://24wbinside.ru/'
                                                    })
                    # Получаем текстовую версию письма из HTML
                    text_content = strip_tags(html_content)
                    EMAIL = env('EMAIL_HOST_USER')

                    # Создаем объект EmailMultiAlternatives
                    email = EmailMultiAlternatives(
                        'Новое бронирование',
                        text_content,
                        EMAIL,
                        [payment.appointment.expert.email]
                    )
                    # Добавляем HTML версию
                    email.attach_alternative(html_content, "text/html")
                    email.send()

            except Exception as e:
                # Если произошла ошибка, откатываем транзакцию
                debug_logger.debug(f"An error occurred: {e}")
                return HttpResponse(status=500)

        return HttpResponse(status=200)


@login_required()
def add_appointment_success_view(request, *args, **kwargs):
    return render(request, "add_appointment_success.html", **kwargs)


@login_required
def checkout_appointment_view(request, *args, **kwargs):
    if request.method == 'POST':
        appointment_id = request.POST['appointment_id']
        try:
            appointment = Appointment.objects.get(pk=appointment_id, client=request.user)
        except Appointment.DoesNotExist:
            raise Http404("Entity does not exist")

        appointment_payment = AppointmentPayment()
        appointment_payment.appointment = appointment
        appointment_payment.summ = appointment.expert.expertprofile.hour_cost
        # appointment_payment.status = AppointmentPayment.AppointmentPaymentStatus.PENDING

        current_base_url = request.scheme + '://' + request.get_host()
        payment = create_yookassa_payment(appointment_payment.summ, current_base_url)

        # debug_logger.debug("#### payment status = " + payment.status)
        # Меняем статус платежа
        appointment_payment.uuid = payment.id
        appointment_payment.save()

        return redirect(payment.confirmation.confirmation_url)
    else:
        appointment = Appointment.objects.get(pk=kwargs['pk'])
        context = {
            "appointment": appointment,
        }

    return render(request, 'checkout_appointment.html', context=context)
