from django.db import models


class AppointmentStatus(models.IntegerChoices):
    NEW = 0, 'Новый'
    СONFIRM = 1, 'Верифицирован'
    DECLIAN = 2, 'Верифицирован'
    CANCEL = 3, 'Верифицирован'
    PAID = 4, 'Верифицирован'


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


class ExpertSchedule(models.Model):
    expert = models.ForeignKey("web.CustomUser", on_delete=models.CASCADE, related_name="expert")
    day_of_week = models.IntegerField(choices=[(i, i) for i in range(7)])
    start_time = models.TimeField()
    end_time = models.TimeField()
