import pytz

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

    localized_appointment_datetime = dfr_serializes.SerializerMethodField()

    def get_localized_appointment_datetime(self, obj):
        request = self.context.get('request')
        user_tz = pytz.timezone(request.user.profile.timezone)
        return obj.appointment_datetime.astimezone(user_tz).strftime("%Y-%m-%d %H:%M")

    class Meta:
        model = Appointment
        fields = ("id", "localized_appointment_datetime", "client", "expert", "status", "created_time", "zoom_link")


class ExpertScheduleSerializer(dfr_serializes.ModelSerializer):
    class Meta:
        model = ExpertSchedule
        fields = ("day_of_week", "start_time", "end_time")


class ExpertScheduleSpecialDaysSerializer(dfr_serializes.ModelSerializer):

    localized_start = dfr_serializes.SerializerMethodField()
    localized_end = dfr_serializes.SerializerMethodField()

    def get_localized_start(self, obj):
        request = self.context.get('request')
        user_tz = pytz.timezone(request.user.profile.timezone)
        return obj.start.astimezone(user_tz).strftime("%Y-%m-%d %H:%M")

    def get_localized_end(self, obj):
        request = self.context.get('request')
        user_tz = pytz.timezone(request.user.profile.timezone)
        return obj.end.astimezone(user_tz).strftime("%Y-%m-%d %H:%M")

    class Meta:
        model = ExpertScheduleSpecialDays
        fields = ("localized_start", "localized_end", "type","id")

