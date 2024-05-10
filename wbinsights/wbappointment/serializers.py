from web.models import CustomUser
from .models import Appointment, ExpertSchedule, ExpertScheduleSpecialDays
from rest_framework import serializers as dfr_serializes


class ClientSerializer(dfr_serializes.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "first_name", "last_name")


class ExpertSerializer(dfr_serializes.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "first_name", "last_name")


class AppointmentSerializer(dfr_serializes.ModelSerializer):
    client = ClientSerializer()
    expert = ExpertSerializer()

    class Meta:
        model = Appointment
        fields = ("id", "appointment_date", "appointment_time", "client", "expert", "status", "created_time")


class ExpertScheduleSerializer(dfr_serializes.ModelSerializer):
    class Meta:
        model = ExpertSchedule
        fields = ("day_of_week", "start_time", "end_time")


class ExpertScheduleSpecialDaysSerializer(dfr_serializes.ModelSerializer):
    start = dfr_serializes.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    end = dfr_serializes.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = ExpertScheduleSpecialDays
        fields = ("start", "end", "type","id")

