from django.forms import formset_factory

from wbappointment.forms import ExpertScheduleForm
from wbappointment.models import ExpertSchedule


def get_expert_schedule_form_set(request):
    ExpertScheduleFormSet = formset_factory(ExpertScheduleForm, extra=0)
    initial_values = [{'day_of_week': day_num + 1, 'start_time': '06:00', 'end_time': '21:00'} for day_num in
                      range(0, 7)]

    if request.user.is_authenticated:
        experts_schedule = ExpertSchedule.objects.filter(expert=request.user).all()

        if len(experts_schedule) != 0:
            initial_values = [
                {'day_of_week': schedule.day_of_week, 'start_time': schedule.start_time.strftime("%H:%M"), 'end_time': schedule.end_time.strftime("%H:%M")} for
                schedule in experts_schedule]

    return ExpertScheduleFormSet(initial=initial_values)
