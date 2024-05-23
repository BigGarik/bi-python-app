from datetime import date, timedelta, datetime, time

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render

from wbappointment.forms import AppointmentForm, SelectAppointmentDateForm
from wbappointment.models import Appointment, AppointmentStatus, ExpertSchedule, AppointmentPayment, \
    ExpertScheduleSpecialDays
from wbappointment.views.yookassa import create_yookassa_payment
from web.models import Expert


@login_required
def add_appointment_view(request, *args, **kwargs):
    expert = Expert.objects.get(pk=kwargs['pk'])

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        # check for existing appointment for this date and time with this expert
        # don't create new one if already exist

        if form.is_valid():

            existAppointment = Appointment.objects.filter(
                expert=expert,
                client=request.user,
                appointment_date=form.cleaned_data['appointment_date'],
                appointment_time=form.cleaned_data['appointment_time'],
                status=AppointmentStatus.NEW
            )

            if existAppointment.exists():
                # If already exist such appointent just work with it
                # No need to create new one
                form = AppointmentForm(request.POST, instance=existAppointment[0])

            new_appointment = form.save(commit=False)
            new_appointment.client = request.user
            new_appointment.expert = expert

            # Получение текущего времени
            #end_time = form.cleaned_data['appointment_time'] + timedelta(hours=1)

            new_appointment.save()
            return redirect('appointment_checkout', pk=new_appointment.id)
    else:
        form = AppointmentForm()
        not_avalable_dates = get_expert_working_dates(expert)
        context = {
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
        if len(expert_schedule) > 0:
            start_time_hour = expert_schedule[0].start_time.hour
            end_time_hour = expert_schedule[0].end_time.hour
            for hour in range(start_time_hour, end_time_hour):
                available_time_slots.append(time(hour=hour, minute=0))

        expert_schedule_special_days = ExpertScheduleSpecialDays.objects.filter(start__date__gte=selected_date,
                                                                                end__date__lte=selected_date).all()
        for special_day in expert_schedule_special_days:
            current_date = special_day.start
            while current_date <= special_day.end:
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
        busyExpertsSlots = Appointment.objects.filter(expert_id=expert_id, appointment_date=selected_date).values_list(
            "appointment_time", flat=True)

        for busy_time in busyExpertsSlots:
            if busy_time in available_time_slots:
                available_time_slots.remove(busy_time)

        return JsonResponse([dt.strftime('%H:%M') for dt in available_time_slots], safe=False)

    return JsonResponse({'errors': dict(form.errors)}, status=400)


def appointment_payment_callback_view(request, *args, **kwargs):
    # Print HTTP method
    print("Method:", request.method)

    # Print request path
    print("Path:", request.path)

    # Print GET parameters
    print("GET parameters:", request.GET)

    # Print POST parameters (if applicable)
    if request.method == "POST":
        print("POST parameters:", request.POST)

    # Print headers
    print("Headers:", dict(request.headers))

    # Print body (if applicable, such as in POST requests)
    print("Body:", request.body.decode('utf-8'))
    return render(request, "add_appointment_success.html", **kwargs)


@login_required()
def add_appointment_success_view(request, *args, **kwargs):
    return render(request, "add_appointment_success.html", **kwargs)


@login_required
def checkout_appointment_view(request, *args, **kwargs):
    if request.method == 'POST':
        appointment_id = request.POST['appointment_id']
        appointment = Appointment.objects.get(pk=appointment_id, client=request.user)

        appointment_payment = AppointmentPayment()
        appointment_payment.appointment = appointment
        appointment_payment.summ = appointment.expert.expertprofile.hour_cost
        #appointment_payment.status = AppointmentPayment.AppointmentPaymentStatus.PENDING

        current_base_url = request.scheme + '://' + request.get_host()
        payment = create_yookassa_payment(appointment_payment.summ, current_base_url)

        appointment_payment.uuid = payment.id
        appointment_payment.save()

        return redirect(payment.confirmation.confirmation_url)
    else:
        appointment = Appointment.objects.get(pk=kwargs['pk'])
        context = {
            "appointment": appointment,
        }

    return render(request, 'checkout_appointment.html', context=context)
