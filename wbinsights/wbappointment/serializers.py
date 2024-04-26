from web.models import CustomUser
from .models import Appointment
from rest_framework import serializers as dfr_serializes


class ClientSerializer(dfr_serializes.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "first_name", "last_name")


class AppointmentSerializer(dfr_serializes.ModelSerializer):
    client = ClientSerializer()

    class Meta:
        model = Appointment
        fields = ("id", "appointment_date", "appointment_time", "client", "status", "created_time")