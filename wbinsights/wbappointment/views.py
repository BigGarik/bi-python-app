from django.contrib.auth.decorators import login_required
from django.contrib.messages import api
from django.shortcuts import render, redirect

from rest_framework import viewsets

from web.models import Expert
from .forms import AppointmentForm
from .models import Appointment
from .serializers import AppointmentTimeSerializer


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
            'not_avalable_dates':not_avalable_dates
        }

    return render(request, 'add_appointment.html', context=context)


@login_required
def checkout_appointment_view(request, *args, **kwargs):

    appointment = Appointment.objects.get(pk=kwargs['pk'])
    if request.method == 'POST':
        return redirect('success')  # assuming you have a success url mapped in your urls.py
    else:

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
