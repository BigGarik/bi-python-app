from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Appointment, ExpertSchedule, AppointmentStatus

from django.utils.translation import gettext as _


def validate_date(date):
    if date < timezone.now().date():
        raise ValidationError("Appointment date cannot be in the past.")


class AppointmentForm(forms.ModelForm):
    hour_choices = [(str(i).zfill(2) + ":00", str(i).zfill(2) + ":00") for i in range(24)]  # hour choices

    appointment_time = forms.ChoiceField(
        choices=hour_choices,
        widget=forms.Select(attrs={'class': 'appointment-form-control', 'disabled': 'disabled'})
    )

    expert = forms.HiddenInput()

    def __init__(self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)
        self.fields['appointment_date'].validators.append(validate_date)

    def clean(self):
        cleaned_data = super().clean()

        expert = cleaned_data.get('expert')
        appointment_date = cleaned_data.get('appointment_date')
        appointment_time = cleaned_data.get('appointment_time')

        # Validation to check there is no booked appointment with
        # this expert on this time in status new older than 10 min
        # current date and time
        now = datetime.now()
        # calculate 10 minutes ago
        ten_minutes_ago = now - timedelta(minutes=10)

        if Appointment.objects.filter(
                expert=expert,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status=AppointmentStatus.NEW,
                created_time__gte=ten_minutes_ago
        ).exists():
            # We can't create this appointment because smobody else alreary booked it
            # ANd we can book it if its no paid in 10 min
            raise forms.ValidationError("An appointment already exists with these details.")

    class Meta:
        model = Appointment
        fields = ['expert', 'appointment_date', 'appointment_time', 'notes']
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

    HOUR_CHOICES = [(f'{hour:02}:00', f'{hour:02}:00') for hour in range(6, 22)]  # Generate choices from 06:00 to 22:00

    start_time = forms.ChoiceField(choices=HOUR_CHOICES, initial=6,  widget=forms.Select(attrs={'class':'form-control form-control-sm'}))
    end_time   = forms.ChoiceField(choices=HOUR_CHOICES, initial=22, widget=forms.Select(attrs={'class':'form-control form-control-sm expert-schedule-form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time:
            if start_time >= end_time:
                raise ValidationError(_("End time must be after start time."))

        return cleaned_data

    class Meta:
        model = ExpertSchedule
        fields = ['day_of_week', 'start_time', 'end_time']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-control form-control-sm'}),
        }


class SelectAppointmentDateForm(forms.Form):
    selected_date = forms.DateField()
    expert_id = forms.IntegerField()