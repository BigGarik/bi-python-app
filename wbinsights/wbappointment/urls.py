from django.urls import path

from wbappointment.views import add_appointment

urlpatterns = [
    # path("", handleIndex, name="index"),
    path("add/<int:pk>/", add_appointment, name="appointment_add")
]