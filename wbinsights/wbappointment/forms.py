from django import forms
from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_date','appointment_time', 'notes']
        widgets = {
            'appointment_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control'
                }),

            'appointment_time': forms.TimeInput(

                attrs={
                    'type': 'time',
                    'step': '3600',
                    'class': 'form-control'
                })
        }
