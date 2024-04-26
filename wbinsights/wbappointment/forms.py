from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Appointment, ExpertSchedule, AppointmentStatus


def validate_date(date):
    if date < timezone.now().date():
        raise ValidationError("Appointment date cannot be in the past.")


class AppointmentForm(forms.ModelForm):
    hour_choices = [(str(i).zfill(2) + ":00", str(i).zfill(2) + ":00") for i in range(24)]  # hour choices

    # hour_choices = [(str(i).zfill(2) + ":" + str(j).zfill(2), str(i).zfill(2) + ":" + str(j).zfill(2)) for i in
    #                 range(24) for j in range(0, 60, 30)]   # with increments of 30 min

    appointment_time = forms.ChoiceField(
        choices=hour_choices,
        widget=forms.Select(attrs={'class': 'appointment-form-control', 'disabled': 'disabled'})
    )

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
                status=AppointmentStatus.NEW.value,
                created_time__gte=ten_minutes_ago
        ).exists():
            raise forms.ValidationError("An appointment already exists with these details.")

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


class SelectAppointmentDateForm(forms.Form):
    selected_date = forms.DateField()
    expert_id = forms.IntegerField()