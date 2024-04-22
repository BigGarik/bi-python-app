from django.urls import path, include
from rest_framework import routers

from wbappointment.views import add_appointment_view, add_appointment_success_view, appointment_payment_callback_view, \
    checkout_appointment_view, get_expert_avalable_timeslots, get_experts_appointment

# AppointmentExpertAvialableTimeForDateView

# router = routers.DefaultRouter("api")
# router.register('expert/availiable/time', AppointmentExpertAvialableTimeForDateView)
#router.register('groups', views.GroupViewSet)

urlpatterns = [
    # path("", handleIndex, name="index"),
    path("add/<int:pk>/", add_appointment_view, name="appointment_add"),
    path("add/success/", add_appointment_success_view, name="appointment_add_success"),
    path("payment/callback/", appointment_payment_callback_view, name="appointment_add_success_callback"),
    path("checkout/<int:pk>/", checkout_appointment_view, name="appointment_checkout"),
    path("available/timeslots/json", get_expert_avalable_timeslots, name="get_expert_avalable_timeslots"),
    path("list/<int:expert_id>/json", get_experts_appointment, name="get_experts_appointment")

    #path("expert/availiable/time/", AppointmentExpertAvialableTimeForDateView.as_view(), name="appointment_available_time_slots"),
]