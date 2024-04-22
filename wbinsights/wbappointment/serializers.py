from rest_framework import serializers
from .models import Appointment


class AppointmentTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['appointment_time']