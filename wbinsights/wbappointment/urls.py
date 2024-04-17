from django.urls import path, include
from rest_framework import routers

from wbappointment.views import add_appointment_view, checkout_appointment_view
# AppointmentExpertAvialableTimeForDateView

# router = routers.DefaultRouter("api")
# router.register('expert/availiable/time', AppointmentExpertAvialableTimeForDateView)
#router.register('groups', views.GroupViewSet)

urlpatterns = [
    # path("", handleIndex, name="index"),
    path("add/<int:pk>/", add_appointment_view, name="appointment_add"),
    path("checkout/<int:pk>/", checkout_appointment_view, name="appointment_checkout"),
    path('api/', include('rest_framework.urls', namespace='rest_framework')),
    #path("expert/availiable/time/", AppointmentExpertAvialableTimeForDateView.as_view(), name="appointment_available_time_slots"),
]