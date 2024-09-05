from django.db.models.functions import TruncTime
from django.forms import modelformset_factory
from django.utils import timezone

from wbappointment.forms import ExpertScheduleForm
from wbappointment.models import ExpertSchedule


def get_expert_schedule_form_set(request):
    user_timezone = request.user.profile.timezone
    timezone.activate(user_timezone)

    experts_schedule = ExpertSchedule.objects.filter(expert=request.user).all()

    if experts_schedule.exists():

        # initial_values = [{
        #     'start_time': row.start_datetime.time().strftime('%H:%M'),
        #     'end_time': row.end_datetime.time().strftime('%H:%M')
        # } for row in experts_schedule]

        expertScheduleFormSet = modelformset_factory(ExpertSchedule,
                                                     form=ExpertScheduleForm, exclude=[], extra=0)

        #return expertScheduleFormSet(initial=initial_values, queryset=experts_schedule)
        return expertScheduleFormSet(queryset=experts_schedule)


    expertScheduleFormSet = modelformset_factory(ExpertSchedule,
                                                 form=ExpertScheduleForm, exclude=[], extra=7)
    initial_values = [{'day_of_week': day_num, 'start_time': '09:00', 'end_time': '18:00'} for day_num in
                      range(1, 8)]

    return expertScheduleFormSet(initial=initial_values, queryset=ExpertSchedule.objects.none())
    #return expertScheduleFormSet(queryset=ExpertSchedule.objects.none())


def get_experts_min_max_hours(request):
    return 0
