from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from wbappointment.forms import ExpertScheduleForm, ExpertScheduleSpecialDaysForm
from wbappointment.models import ExpertSchedule, ExpertScheduleSpecialDays, Appointment
from wbappointment.serializers import AppointmentSerializer, ExpertScheduleSerializer, \
    ExpertScheduleSpecialDaysSerializer


@require_POST
@login_required()
def add_expert_schedule_view(request):
    queryset = ExpertSchedule.objects.filter(expert=request.user)
    ExpertScheduleFormSet = modelformset_factory(ExpertSchedule, form=ExpertScheduleForm, exclude=[])

    formset = ExpertScheduleFormSet(request.POST, queryset=queryset)
    if formset.is_valid():
        saved_objects = []
        for form in formset.forms:
            expert_schedule = form.save(commit=False)
            expert_schedule.expert = request.user
            expert_schedule.save()
            saved_objects.append(expert_schedule)
        # json_data = serialize('json', saved_objects)
        # {'result': "success", 'data': json_data}, status=200)

    #return redirect(request.POST['origin-path'])


    return  JsonResponse({'result': "success"}, status=200)


@login_required
@require_POST
def add_appointment_range_view(request, *args, **kwargs):
    expertScheduleSpecialDaysForm = ExpertScheduleSpecialDaysForm(request.POST)

    if expertScheduleSpecialDaysForm.is_valid():
        existSpecialDay = ExpertScheduleSpecialDays.objects.filter(expert=request.user,
                                                 start=expertScheduleSpecialDaysForm.cleaned_data['start'],
                                                 end=expertScheduleSpecialDaysForm.cleaned_data['end'])

        if existSpecialDay.exists():
            expertScheduleSpecialDaysForm = ExpertScheduleSpecialDaysForm(request.POST, instance=existSpecialDay[0])

        expertScheduleSpecialDays = expertScheduleSpecialDaysForm.save(commit=False)
        expertScheduleSpecialDays.expert = request.user
        expertScheduleSpecialDays.save()

        return JsonResponse({'result': 'success'})

    #return redirect(request.POST['origin-path'])

    return JsonResponse({'result': 'error', 'errors': ''})


def get_start_of_week():
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    return start_of_week.date()

@login_required
def get_experts_appointment(request, *args, **kwargs):
    selected_expert = kwargs['expert_id']

    appointments = Appointment.objects.filter(expert_id=selected_expert)


    extra_dates = ExpertScheduleSpecialDays.objects.filter(expert_id=selected_expert, start__gte=get_start_of_week())
    expert_schedule = ExpertSchedule.objects.filter(expert_id=selected_expert)
    return JsonResponse({'data': {'appointments': AppointmentSerializer(appointments, many=True).data,
                                  'extra_dates': ExpertScheduleSpecialDaysSerializer(extra_dates, many=True).data,
                                  'schedule': ExpertScheduleSerializer(expert_schedule, many=True).data}})


@login_required
def get_clients_appointment(request, *args, **kwargs):
    selected_client = kwargs['client_id']
    appointments = Appointment.objects.filter(client_id=selected_client)
    return JsonResponse({'data': AppointmentSerializer(appointments, many=True).data})