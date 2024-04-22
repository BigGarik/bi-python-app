from django import forms
from .models import Appointment


class AppointmentForm(forms.ModelForm):

    hour_choices = [(str(i).zfill(2) + ":00", str(i).zfill(2) + ":00") for i in range(24)]  # hour choices

    # hour_choices = [(str(i).zfill(2) + ":" + str(j).zfill(2), str(i).zfill(2) + ":" + str(j).zfill(2)) for i in
    #                 range(24) for j in range(0, 60, 30)]   # with increments of 30 min

    appointment_time = forms.ChoiceField(
        choices=hour_choices,
        widget=forms.Select(attrs={'class': 'appointment-form-control'})
    )

    class Meta:
        model = Appointment
        fields = ['appointment_date', 'appointment_time', 'notes']
        widgets = {
            'appointment_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'appointment-form-control'
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'appointment-form-control auto-resize',
                    'rows': 6
                }
            )
        }
