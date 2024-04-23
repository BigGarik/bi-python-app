from django.contrib.auth.decorators import login_required
from django.contrib.messages import api
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from rest_framework import viewsets

from web.models import Expert, CustomUser
from .forms import AppointmentForm
from .models import Appointment, AppointmentStatus, AppointmentPayment
from .serializers import AppointmentTimeSerializer

from yookassa import Configuration, Payment
import uuid

from django.core import serializers
from rest_framework import serializers as dfr_serializes


Configuration.account_id = '372377'
Configuration.secret_key = 'test_GweuBNA4H85vWxRCLXLsz7gJLX2lA_YJ2GjYGpRBxLw'


# Create your views here.

@login_required
def add_appointment_view(request, *args, **kwargs):
    expert = Expert.objects.get(pk=kwargs['pk'])
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
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
    selected_expert = request.GET['expert']
    selected_date = request.GET['date']
    timeslot = []
    if selected_date == '2024-04-10':
        timeslot = ['11:00',
                    '13:00',
                    '16:00',
                    '17:00']

    if selected_date == '2024-04-11':
        timeslot = ['10:00',
                    '14:00',
                    '15:00',
                    '16:00']
    return JsonResponse(timeslot, safe=False)

class ClientSerializer(dfr_serializes.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id","first_name", "last_name")

class AppointmentSerializer(dfr_serializes.ModelSerializer):
    client = ClientSerializer()
    class Meta:
        model = Appointment
        fields = ("appointment_date", "appointment_time", "client")

def get_experts_appointment(request, *args, **kwargs):
    selected_expert = kwargs['expert_id']
    appointments = Appointment.objects.filter(expert_id=selected_expert)

    return JsonResponse({'data':AppointmentSerializer(appointments, many=True).data})

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

        #if not appointment:
         #throw exeption

        appointment_payment = AppointmentPayment()
        appointment_payment.appointment = appointment
        appointment_payment.summ = appointment.expert.expertprofile.hour_cost


        # Create payment
        # res = Payment.create(
        #     {
        #         "amount": {
        #             "value": appointment.expert.expertprofile.hour_cost,
        #             "currency": "RUB"
        #         },
        #         "confirmation": {
        #             "type": "redirect",
        #             "return_url": "https://0f84-176-74-217-47.ngrok-free.app/appointment/add/success"
        #         },
        #         "capture": True,
        #         "description": "Оплата услуги консультации",
        #         "metadata": {
        #             'orderNumber': appointment.id
        #         },
        #         "receipt": {
        #             "customer": {
        #                 "full_name": appointment.client.last_name + ' ' +appointment.client.last_name ,
        #                 "email": appointment.client.email,
        #                 "phone": appointment.client.phone_number
        #                 # "inn": "6321341814"
        #             },
        #             "items": [
        #                 {
        #                     "description": "Оплата услуги консультации",
        #                     "quantity": "1.00",
        #                     "amount": {
        #                         "value": appointment.expert.expertprofile.hour_cost,
        #                         "currency": "RUB"
        #                     },
        #                     "vat_code": "2",
        #                     "payment_mode": "full_payment",
        #                     "payment_subject": "commodity",
        #                     "country_of_origin_code": "CN",
        #                     "product_code": "44 4D 01 00 21 FA 41 00 23 05 41 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 12 00 AB 00",
        #                     "customs_declaration_number": "10714040/140917/0090376",
        #                     "excise": "20.00",
        #                     "supplier": {
        #                         "name": "string",
        #                         "phone": "string",
        #                         "inn": "string"
        #                     }
        #                 },
        #             ]
        #         }
        #     }
        # )

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
        # var_dump.var_dump(res)
    else:
        appointment = Appointment.objects.get(pk=kwargs['pk'])
        context = {
            "appointment": appointment,
        }

    return render(request, 'checkout_appointment.html', context=context)


# @api.get('/appointments/expert/availiable/time/{int:expert_id}/{str:app_date}/')
# def get_available_expert_time_for_date(request, expert_id:int, app_date:str):
#     return {'expert_id':expert_id}


class AppointmentExpertAvialableTimeForDateView(viewsets.ModelViewSet):
    serializer_class = AppointmentTimeSerializer

    def get_queryset(self):
        expert_id = self.request.query_params.get('expert_pk', None)
        appointment_date = self.request.query_params.get('app_date', None)
        queryset = Appointment.objects.filter(expert_id=expert_id, appointment_date=appointment_date)
        return queryset
