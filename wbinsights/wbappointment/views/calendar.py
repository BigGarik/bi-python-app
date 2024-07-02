from django.contrib.auth.decorators import login_required

from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

from wbappointment.forms import *
from wbappointment.models import *
from wbappointment.serializers import AppointmentSerializer, ExpertScheduleSpecialDaysSerializer


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

        redirect_url = request.POST['origin-path']
        if request.POST['origin-query'] != "":
            redirect_url += '?' + request.POST['origin-query']
        return redirect(redirect_url)

    return JsonResponse({'result': "success"}, status=200)


@login_required
@require_POST
def add_appointment_range_view(request, *args, **kwargs):
    expertScheduleSpecialDaysForm = ExpertScheduleSpecialDaysForm(request.POST)

    if expertScheduleSpecialDaysForm.is_valid():
        existSpecialDay = ExpertScheduleSpecialDays.objects.filter(expert=request.user,
                                                                   start=expertScheduleSpecialDaysForm.cleaned_data[
                                                                       'start'],
                                                                   end=expertScheduleSpecialDaysForm.cleaned_data[
                                                                       'end'])

        if existSpecialDay.exists():
            expertScheduleSpecialDaysForm = ExpertScheduleSpecialDaysForm(request.POST, instance=existSpecialDay[0])

        expertScheduleSpecialDays = expertScheduleSpecialDaysForm.save(commit=False)
        expertScheduleSpecialDays.expert = request.user
        expertScheduleSpecialDays.save()

        return JsonResponse({'result': 'success'})

    return JsonResponse({'result': 'error', 'errors': ''})


@login_required
@require_POST
def delete_appointment_range_view(request, *args, **kwargs):
    int_range_id = request.POST['range_id']

    if int_range_id.isdigit():
        expertScheduleSpecialDays = ExpertScheduleSpecialDays.objects.filter(pk=int_range_id, expert=request.user)
        if len(expertScheduleSpecialDays) > 0:
            expertScheduleSpecialDays[0].delete()
            return JsonResponse({'result': 'success'})

    return JsonResponse({'result': 'error'})


def get_start_of_week():
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    return start_of_week.date()


@login_required
def get_experts_appointment(request, *args, **kwargs):
    selected_expert = request.user

    calendarForm = CalendarEventForm(request.GET)

    if calendarForm.is_valid():
        start_date = calendarForm.cleaned_data['start']
        end_date = calendarForm.cleaned_data['end']

        # Возвращаем все что будет отображаться на календаре
        appointments_as_expert = Appointment.objects.filter(expert=selected_expert,
                                                            appointment_date__gte=start_date.date(),
                                                            appointment_date__lte=end_date.date())
        appointments_as_client = Appointment.objects.filter(client=selected_expert,
                                                            appointment_date__gte=start_date.date(),
                                                            appointment_date__lte=end_date.date())

        extra_dates = ExpertScheduleSpecialDays.objects.filter(expert_id=selected_expert,
                                                               start__gte=get_start_of_week())

        expert_schedule = ExpertSchedule.objects.filter(expert_id=selected_expert)
        schedule_dates = []
        for schedule_day in expert_schedule:
            if not schedule_day.is_work_day:
                continue
            schedule_date = start_date + timedelta(days=schedule_day.day_of_week - 1)

            schedule_datetime_start = datetime.combine(schedule_date, schedule_day.start_time)
            schedule_datetime_end = datetime.combine(schedule_date, schedule_day.end_time)

            schedule_dates.append({'start':schedule_datetime_start.strftime("%Y-%m-%d %H:%M"), 'end':schedule_datetime_end.strftime("%Y-%m-%d %H:%M")})

        return JsonResponse(
            {'data':
                {
                    'appointments': {
                        'as_expert':  AppointmentSerializer(appointments_as_expert, many=True).data,
                        'as_client':  AppointmentSerializer(appointments_as_client, many=True).data,
                    },
                    'extra_dates': ExpertScheduleSpecialDaysSerializer(extra_dates, many=True).data,
                    'schedule': schedule_dates
                }
            })


@login_required
def get_clients_appointment(request, *args, **kwargs):
    appointments_as_client = Appointment.objects.filter(client_id=request.user.id)

    return JsonResponse(
        {'data':
            {
                'appointments': {
                    'as_client': AppointmentSerializer(appointments_as_client, many=True).data,
                }
            }
        })