from django.urls import path

from wbappointment.views.appointments import add_appointment_view, checkout_appointment_view, \
    get_expert_available_timeslots, add_appointment_success_view, appointment_payment_callback_view

from wbappointment.views.calendar import add_expert_schedule_view, add_appointment_range_view, get_experts_appointment, \
    get_clients_appointment

urlpatterns = [
    # path("", handleIndex, name="index"),
    path("add/<int:pk>/", add_appointment_view, name="appointment_add"),

    path("checkout/<int:pk>/", checkout_appointment_view, name="appointment_checkout"),
    path("available/timeslots/json", get_expert_available_timeslots, name="get_expert_avalable_timeslots"),
    path("add/success/", add_appointment_success_view, name="appointment_add_success"),
    path("payment/callback/", appointment_payment_callback_view, name="appointment_add_success_callback"),

    path("calendar/add/schedule/", add_expert_schedule_view, name="add_calendar_schedule"),
    path("calendar/add/range/", add_appointment_range_view, name="add_calendar_range"),
    path("calendar/expert/json", get_experts_appointment, name="get_experts_appointment"),
    path("calendar/client/json", get_clients_appointment, name="get_clients_appointment")

    #path("expert/availiable/time/", AppointmentExpertAvialableTimeForDateView.as_view(), name="appointment_available_time_slots"),
]