from django import forms
from .models import Appointment, ExpertSchedule


class AppointmentForm(forms.ModelForm):

    hour_choices = [(str(i).zfill(2) + ":00", str(i).zfill(2) + ":00") for i in range(24)]  # hour choices

    # hour_choices = [(str(i).zfill(2) + ":" + str(j).zfill(2), str(i).zfill(2) + ":" + str(j).zfill(2)) for i in
    #                 range(24) for j in range(0, 60, 30)]   # with increments of 30 min

    appointment_time = forms.ChoiceField(
        choices=hour_choices,
        widget=forms.Select(attrs={'class': 'appointment-form-control','disabled':'disabled'})
    )

    class Meta:
        model = Appointment
        fields = ['appointment_date', 'appointment_time', 'notes']
        widgets = {
            'appointment_date': forms.HiddenInput(
                attrs={

                    'class': 'appointment-form-control1'
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'appointment-form-control auto-resize',
                    'rows': 6
                }
            )
        }

class ExpertScheduleForm(forms.ModelForm):

    class Meta:
        model = ExpertSchedule
        fields = ['day_of_week', 'start_time', 'end_time']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': ''}),
            'start_time': forms.TimeInput(attrs={'class': 'expert-schedule-form-control'}),
            'end_time': forms.TimeInput(attrs={'class': 'expert-schedule-form-control'}),
        }
