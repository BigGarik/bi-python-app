from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.serializers import serialize
from django.db.models import Max, Min
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from web.models import Expert
from .forms import AppointmentForm, SelectAppointmentDateForm, ExpertScheduleForm
from .models import Appointment, AppointmentStatus, AppointmentPayment, ExpertSchedule
from .serializers import AppointmentSerializer

from yookassa import Configuration, Payment
import uuid

from django.forms import formset_factory, modelformset_factory
from datetime import date, timedelta

Configuration.account_id = '372377'
Configuration.secret_key = 'test_GweuBNA4H85vWxRCLXLsz7gJLX2lA_YJ2GjYGpRBxLw'


@login_required
def add_appointment_view(request, *args, **kwargs):
    expert = Expert.objects.get(pk=kwargs['pk'])

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        # check for existing appointment for this date and time with this expert
        # don't create new one if already exist
        existAppointment = Appointment.objects.filter(
            expert=expert,
            client=request.user,
            appointment_date=form.data['appointment_date'],
            appointment_time=form.data['appointment_time'],
            status=AppointmentStatus.NEW
        )

        if existAppointment.exists():
            # If already exist such appointent just work with it
            # No need to create new one
            form = AppointmentForm(request.POST, instance=existAppointment[0])

        if form.is_valid():
            new_appointment = form.save(commit=False)
            new_appointment.client = request.user
            new_appointment.expert = expert
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


@require_POST
def add_expert_schedule_view(request):
    queryset = ExpertSchedule.objects.filter(expert=request.user)
    ExpertScheduleFormSet = modelformset_factory(ExpertSchedule, form=ExpertScheduleForm, exclude=[])

    formset = ExpertScheduleFormSet(request.POST, queryset=queryset)
    if formset.is_valid():
        saved_objects = []
        for form in formset.forms:
            expert_schedule = form.save(commit=False)
            expert_schedule.expert = request.user
            expert_schedule.save()
            saved_objects.append(expert_schedule)
        #json_data = serialize('json', saved_objects)
        # {'result': "success", 'data': json_data}, status=200)

    return redirect(request.POST['origin-path'])

# return  JsonResponse({'result': "success"}, status=200)


def get_expert_working_dates(expert):
    calendar_period = 120  # days

    start_date = date.today()
    end_date = start_date + timedelta(days=calendar_period)

    expert_schedule = ExpertSchedule.objects.filter(expert=expert).all()

    expert_schedule_working_days_numbers = []

    for day in expert_schedule:
        expert_schedule_working_days_numbers.append(day.day_of_week)

    not_working_dates = []

    for i in range(calendar_period + 1):
        day = start_date + timedelta(days=i)

        if (day.weekday() not in expert_schedule_working_days_numbers):
            not_working_dates.append(day.strftime("%Y-%m-%d"))

    return {'data': {"start": start_date.strftime("%Y-%m-%d"), "end": end_date.strftime("%Y-%m-%d"),
                     "not_working_dates": not_working_dates}}


@login_required()
def get_expert_avalable_timeslots(request):
    form = SelectAppointmentDateForm(request.GET)

    if form.is_valid():

        expert_id = form.cleaned_data['expert_id']
        selected_date = form.cleaned_data['selected_date']

        # get available expert's slot for certain date
        busyExpertsSlots = (Appointment.objects.filter(
            expert_id=expert_id,
            appointment_date=selected_date
        ).values_list("appointment_time", flat=True))

        # transform busy expert's slots to array of string
        busy_experts_str_slots = [dt.strftime('%H:%M') for dt in busyExpertsSlots]

        # get expert's schedule for certain day (+1 because in db schedule's day number starts from 1)
        expert_schedule = ExpertSchedule.objects.filter(expert_id=expert_id,
                                                        day_of_week=selected_date.weekday() + 1).all()

        start_time = 9
        end_time = 18

        if len(expert_schedule) > 0:
            start_time = expert_schedule[0].start_time.hour
            end_time = expert_schedule[0].end_time.hour

        timeslot = [(f'{hour:02}:00') for hour in
                    range(start_time, end_time)]  # Generate choices from start_time to end_time

        # exclude from all slots already busy slots
        available_timeslots = [slot for slot in timeslot if slot not in busy_experts_str_slots]

        return JsonResponse(available_timeslots, safe=False)

    return JsonResponse({'errors': dict(form.errors)}, status=400)


@login_required
def get_experts_appointment(request, *args, **kwargs):
    selected_expert = kwargs['expert_id']
    appointments = Appointment.objects.filter(expert_id=selected_expert)
    return JsonResponse({'data': AppointmentSerializer(appointments, many=True).data})


def get_clients_appointment(request, *args, **kwargs):
    selected_client = kwargs['client_id']
    appointments = Appointment.objects.filter(client_id=selected_client)
    return JsonResponse({'data': AppointmentSerializer(appointments, many=True).data})


def appointment_payment_callback_view(request, *args, **kwargs):
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

        payment = Payment.create({
            "amount": {
                "value": appointment_payment.summ,
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://0f84-176-74-217-47.ngrok-free.app/appointment/add/success"
            },
            "capture": True,
            "description": "Оплата услуги консультации "
        }, uuid.uuid4())

        appointment_payment.uuid = payment.id
        appointment_payment.save()

        p_res = payment.confirmation

        return redirect(p_res.confirmation_url)
    else:
        appointment = Appointment.objects.get(pk=kwargs['pk'])
        context = {
            "appointment": appointment,
        }

    return render(request, 'checkout_appointment.html', context=context)
