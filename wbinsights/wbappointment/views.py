from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render, redirect

from rest_framework import viewsets

from web.models import Expert, CustomUser
from .forms import AppointmentForm, SelectAppointmentDateForm
from .models import Appointment, AppointmentStatus, AppointmentPayment
from .serializers import AppointmentTimeSerializer

from yookassa import Configuration, Payment
import uuid

from django.core import serializers
from rest_framework import serializers as dfr_serializes

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

        if len(existAppointment) > 0:
            form = AppointmentForm(request.POST, instance=existAppointment[0])

        if form.is_valid():
            new_appointment = form.save(commit=False)
            new_appointment.client = request.user
            new_appointment.expert = expert
            new_appointment.save()
            return redirect('appointment_checkout', pk=new_appointment.id)
    else:
        form = AppointmentForm()
        not_avalable_dates = ['18.04.2024', '19.04.2024']
        context = {
            "expert": expert,
            'form': form,
            'not_avalable_dates': not_avalable_dates
        }



    return render(request, 'add_appointment.html', context=context)


def get_expert_avalable_timeslots(request):
    form = SelectAppointmentDateForm(request.GET)

    if form.is_valid():
        # get available expert's slot for certain date
        busyExpertsSlots = (Appointment.objects.filter(
            expert_id=form.cleaned_data['expert_id'],
            appointment_date=form.cleaned_data['selected_date']
        ).values_list("appointment_time",flat=True))

        # transform busy expert's slots to array of string
        busy_experts_str_slots = [dt.strftime('%H:%M') for dt in busyExpertsSlots]

        timeslot = [
            '09:00',
            '10:00',
            '11:00',
            '12:00',
            '13:00',
            '14:00',
            '15:00',
            '16:00',
            '17:00',
            '18:00'
        ]

        # exclude from all slots already busy slots
        available_timeslots = [slot for slot in timeslot if slot not in busy_experts_str_slots]

        return JsonResponse(available_timeslots, safe=False)

    return JsonResponse({'errors': dict(form.errors)}, status=400)


class ClientSerializer(dfr_serializes.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "first_name", "last_name")


class AppointmentSerializer(dfr_serializes.ModelSerializer):
    client = ClientSerializer()

    class Meta:
        model = Appointment
        fields = ("id", "appointment_date", "appointment_time", "client")


def get_experts_appointment(request, *args, **kwargs):
    selected_expert = kwargs['expert_id']
    appointments = Appointment.objects.filter(expert_id=selected_expert)

    return JsonResponse({'data': AppointmentSerializer(appointments, many=True).data})


def get_clients_appointment(request, *args, **kwargs):
    selected_client = kwargs['client_id']
    appointments = Appointment.objects.filter(cleint_id=selected_client)
    data = serializers.serialize("json", appointments, fields=["appointment_date", "appointment_time", "client"])
    return JsonResponse(data, safe=False)


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
