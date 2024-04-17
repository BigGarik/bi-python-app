from django.db import models

# Create your models here.
class Appointment(models.Model):
    expert = models.ForeignKey("CustomUser", on_delete=models.CASCADE)
    client = models.ForeignKey("CustomUser", on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=50)
    zoom_link = models.CharField(null=True)
    notes = models.TextField(null=True, blank=True)
    class Meta:
        db_table = "appointment"
