from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from yookassa import Payment

from wbappointment.forms import AppointmentForm, SelectAppointmentDateForm
from wbappointment.models import Appointment, AppointmentStatus, ExpertSchedule, AppointmentPayment
from wbappointment.views.yookassa import create_yookassa_payment
from web.models import Expert


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

            # Получение текущего времени
            end_time = form.data['appointment_time'] + timedelta(hours=1)

            new_appointment.timeslot = (form.data['appointment_date'] + ' ' + form.data['appointment_time'], form.data['appointment_date'] + ' ' + end_time)
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

        payment = create_yookassa_payment(appointment_payment.summ)

        appointment_payment.uuid = payment.id
        appointment_payment.save()

        return redirect(payment.confirmation.confirmation_url)
    else:
        appointment = Appointment.objects.get(pk=kwargs['pk'])
        context = {
            "appointment": appointment,
        }

    return render(request, 'checkout_appointment.html', context=context)



