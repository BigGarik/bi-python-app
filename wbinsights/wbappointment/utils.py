from django.forms import formset_factory, modelformset_factory

from wbappointment.forms import ExpertScheduleForm
from wbappointment.models import ExpertSchedule


def get_expert_schedule_form_set(request):
    experts_schedule = ExpertSchedule.objects.filter(expert=request.user)

    if experts_schedule.exists():
        expertScheduleFormSet = modelformset_factory(ExpertSchedule,
                                                     form=ExpertScheduleForm, exclude=[], extra=0)
        return expertScheduleFormSet(queryset=experts_schedule)

    expertScheduleFormSet = modelformset_factory(ExpertSchedule,
                                                 form=ExpertScheduleForm, exclude=[], extra=7)
    initial_values = [{'day_of_week': day_num + 1, 'start_time': '09:00:00', 'end_time': '18:00:00'} for day_num in
                      range(0, 7)]
    return expertScheduleFormSet(initial=initial_values)


def get_experts_min_max_hours(request):
    return 0
