from django.forms import formset_factory

from wbappointment.forms import ExpertScheduleForm


def get_expert_schedule_form_set():
    ExpertScheduleFormSet = formset_factory(ExpertScheduleForm, extra=0)
    initial_values = [{'day_of_week': day_num + 1, 'start_time': '06:00', 'end_time': '21:00'} for day_num in
                      range(0, 7)]
    return ExpertScheduleFormSet(initial=initial_values)
