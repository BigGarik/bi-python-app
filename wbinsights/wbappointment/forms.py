import pytz
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Appointment, ExpertSchedule, AppointmentStatus, ExpertScheduleSpecialDays

from django.utils.translation import gettext as _


def validate_date(date):
    if date < timezone.now().date():
        raise ValidationError("Appointment date cannot be in the past.")


class AppointmentForm(forms.ModelForm):

    appointment_date = forms.DateField(
        widget=forms.HiddenInput(),
        required = True
    )

    appointment_time = forms.TimeField(
        widget=forms.HiddenInput(),
        required=True
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

        if appointment_date is None:
            raise forms.ValidationError("appointment_date must not be empty")

        if appointment_time is None:
            raise forms.ValidationError("appointment_time must not be empty")

        # Validation to check there is no booked appointment with
        # this expert on this time in status new older than 10 min
        # current date and time
        now = datetime.now()
        # calculate 10 minutes ago
        ten_minutes_ago = now - timedelta(minutes=10)

        if Appointment.objects.filter(
                expert=expert,
                appointment_datetime=datetime.combine(appointment_date, appointment_time),
                status=AppointmentStatus.NEW,
                created_time__gte=ten_minutes_ago
        ).exists():
            # We can't create this appointment because smobody else alreary booked it
            # ANd we can book it if its no paid in 10 min
            raise forms.ValidationError("An appointment already exists with these details.")

    class Meta:
        model = Appointment
        fields = ['expert', 'notes']
        widgets = {
            'notes': forms.Textarea(
                attrs={
                    'class': 'appointment-form-control auto-resize',
                    'rows': 6
                }
            )
        }


class CalendarEventForm(forms.Form):
    start = forms.DateTimeField()
    end = forms.DateTimeField()


class ExpertScheduleForm(forms.ModelForm):
    HOUR_CHOICES = [(f'{hour:02}:00', f'{hour:02}:00') for hour in
                    range(6, 24)]  # Generate choices from 06:00 to 22:00

    id = forms.HiddenInput()

    start_time = forms.TimeField(
        widget=forms.Select(
            choices=HOUR_CHOICES,
            attrs={'class': 'form-control form-control-sm'}
        ),
        input_formats=['%H:%M']
    )

    end_time = forms.TimeField(
        widget=forms.Select(
            choices=HOUR_CHOICES,
            attrs={'class': 'form-control form-control-sm'}
        ),
        input_formats=['%H:%M']
    )

    is_work_day = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            # Инициализируйте поля start_time и end_time из datetime_field

            #Получаем timezone Пользователя
            target_timezone = self.instance.expert.profile.timezone
            local_tz = pytz.timezone(target_timezone)

            start_time = self.instance.start_datetime.astimezone(local_tz).time().strftime('%H:%M')
            end_time = self.instance.end_datetime.astimezone(local_tz).time().strftime('%H:%M')

            self.fields['start_time'].initial = start_time
            self.fields['end_time'].initial = end_time
        else:
            self.fields['start_time'].initial = '09:00'
            self.fields['end_time'].initial = '18:00'

    def clean(self):
        cleaned_data = super().clean()

        start_time = self.cleaned_data.get("start_time")
        end_time = self.cleaned_data.get("end_time")

        if start_time and end_time:
            if start_time >= end_time:
                raise ValidationError(_("Начальное время должно быть раньше конечного"))

        return cleaned_data

    class Meta:
        model = ExpertSchedule
        fields = ['is_work_day', 'day_of_week', 'id', "start_time"]
        widgets = {
            'day_of_week': forms.HiddenInput(attrs={'class': 'form-control form-control-sm'}),
        }


class SelectAppointmentDateForm(forms.Form):
    selected_date = forms.DateField()
    expert_id = forms.IntegerField()


class ExpertScheduleSpecialDaysForm(forms.ModelForm):
    type_choices = [(choice_id, choice_name) for choice_id, choice_name in ExpertScheduleSpecialDays.SPECIAL_DAY_TYPE]

    type = forms.ChoiceField(choices=type_choices)
    start = forms.DateTimeField()
    end = forms.DateTimeField()

    class Meta:
        model = ExpertScheduleSpecialDays
        fields = ['start', 'end', 'type']
