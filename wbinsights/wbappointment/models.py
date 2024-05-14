from django.db import models
from django.db.models import UniqueConstraint

from django.contrib.postgres.fields import DateTimeRangeField
from django.utils import timezone



class AppointmentStatus(models.IntegerChoices):
    NEW = 0, 'Новый'
    СONFIRM = 1, 'Подтвержден'
    DECLINE = 2, 'Отклонен'
    CANCEL = 3, 'Отменен'
    PAID = 4, 'Оплачен'


class Appointment(models.Model):
    expert = models.ForeignKey("web.CustomUser", on_delete=models.CASCADE, related_name="expert_appointments")
    client = models.ForeignKey("web.CustomUser", on_delete=models.CASCADE, related_name="client_appointments")
    created_time = models.DateTimeField(auto_now_add=True)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.IntegerField(default=AppointmentStatus.NEW, choices=AppointmentStatus.choices)
    zoom_link = models.CharField(null=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "appointment"
        constraints = [UniqueConstraint(fields=['expert', 'appointment_date', 'appointment_time', 'status'],
                                        name='unique_experts_appointment')]


class AppointmentPayment(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="payment")
    summ = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)

    class AppointmentPaymentStatus(models.IntegerChoices):
        PENDING = 0, 'Ожидание'
        COMPLETED = 1, 'Оплачено'
        CANCELED = 2, 'Отменено'

    status = models.IntegerField(default=AppointmentPaymentStatus.PENDING, choices=AppointmentPaymentStatus.choices)
    uuid = models.UUIDField()


# TODO add restriction day_of_week - expert unique
class ExpertSchedule(models.Model):
    expert = models.ForeignKey("web.CustomUser", on_delete=models.CASCADE, related_name="expert")

    DAY_CHOICES = [
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
        (7, 'Sunday'),
    ]

    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_work_day = models.BooleanField(default=True, )

    class Meta:
        constraints = [UniqueConstraint(fields=['expert', 'day_of_week'],
                                        name='unique_experts_schedule')]


class ExpertScheduleSpecialDays(models.Model):
    expert = models.ForeignKey("web.CustomUser", on_delete=models.CASCADE, related_name="_expert")
    start = models.DateTimeField()
    end = models.DateTimeField()

    SPECIAL_DAY_TYPE = [
        (0, 'Unavailable'),
        (1, 'Available'),
    ]
    type = models.IntegerField(choices=SPECIAL_DAY_TYPE)
