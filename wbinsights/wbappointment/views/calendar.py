from datetime import time

from django.contrib.auth.decorators import login_required

from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.timezone import make_naive
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

        user_timezone = request.user.profile.timezone
        timezone.activate(user_timezone)

        for form in formset.forms:
            expert_schedule = form.save(commit=False)

            start_datetime_obj = datetime.combine(datetime.today(), form.cleaned_data['start_time'])
            end_datetime_obj = datetime.combine(datetime.today(), form.cleaned_data['end_time'])

            expert_schedule.start_datetime = timezone.make_aware(start_datetime_obj, timezone.get_current_timezone())
            expert_schedule.end_datetime = timezone.make_aware(end_datetime_obj, timezone.get_current_timezone())

            expert_schedule.expert = request.user
            expert_schedule.save()
            saved_objects.append(expert_schedule)

        timezone.deactivate()

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

        user_tz = pytz.timezone(request.user.profile.timezone)

        start_datetime = user_tz.localize(make_naive(expertScheduleSpecialDaysForm.cleaned_data['start']))
        end_datetime = user_tz.localize(make_naive(expertScheduleSpecialDaysForm.cleaned_data['end']))

        existSpecialDay = ExpertScheduleSpecialDays.objects.filter(expert=request.user,
                                                                   start=start_datetime,
                                                                   end=end_datetime)

        if existSpecialDay.exists():
            expertScheduleSpecialDaysForm = ExpertScheduleSpecialDaysForm(request.POST, instance=existSpecialDay[0])

        expertScheduleSpecialDays = expertScheduleSpecialDaysForm.save(commit=False)
        expertScheduleSpecialDays.start = start_datetime
        expertScheduleSpecialDays.end = end_datetime
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
        start_date = make_naive(calendarForm.cleaned_data['start'])
        end_date = make_naive(calendarForm.cleaned_data['end'])

        # Возвращаем все что будет отображаться на календаре
        appointments_as_expert = Appointment.objects.filter(expert=selected_expert,
                                                            appointment_datetime__gte=start_date.date(),
                                                            appointment_datetime__lte=end_date.date())

        appointments_as_client = Appointment.objects.filter(client=selected_expert,
                                                            appointment_datetime__gte=start_date.date(),
                                                            appointment_datetime__lte=end_date.date())

        extra_dates = ExpertScheduleSpecialDays.objects.filter(expert_id=selected_expert,
                                                               start__gte=get_start_of_week())

        #Разбиваем все диапазоны экстрадат на диапазоны с часовым интервалом
        #Например 2024-09-03 12:00 - 2024-09-03 14:00 олжен превратится в два диапазона [2024-09-03 12:00 - 2024-09-03 13:00, 2024-09-03 13:00 - 2024-09-03 14:00]
        processed_extra_dates = []
        for e_date in extra_dates:
            current = e_date.start
            end_datetime = e_date.end
            while current < end_datetime:
                next_interval = current
                processed_extra_date = ExpertScheduleSpecialDays()
                processed_extra_date.start = next_interval
                processed_extra_date.type = e_date.type
                processed_extra_dates.append(processed_extra_date)
                current = next_interval + timedelta(hours=1)

        expert_schedule = ExpertSchedule.objects.filter(expert_id=selected_expert)

        target_timezone = request.user.profile.timezone
        local_tz = pytz.timezone(target_timezone)

        schedule_dates = []
        for schedule_day in expert_schedule:

            schedule_date = start_date + timedelta(days=schedule_day.day_of_week - 1)

            filtered_processed_extra_dates = [extra_date for extra_date in processed_extra_dates if
                                              extra_date.start.date() == schedule_date.date()]

            #Тут проходим (по сути фильтруем) только по рабочим дням
            if schedule_day.is_work_day:
                # Разбиваем все диапазон конкретного дня расписания на диапазоны с часовым интервалом
                for i in range(schedule_day.start_datetime.time().hour, schedule_day.end_datetime.time().hour):
                    start_time = i
                    end_time = start_time + 1

                    schedule_datetime_start = datetime.combine(schedule_date, time(start_time, 0),
                                                               tzinfo=pytz.utc).astimezone(local_tz)

                    #временной интервал, который может быть доступным и недоступным для брони и совпадает с расписанием
                    extra_slot = None

                    #Проверяем текущий часовой диапозан среди диапазонов экстрадат, и не добавляем если такой имеется
                    #экстрадатах с типом = 0 (Недоступно для бронирования)
                    for e_date in filtered_processed_extra_dates:
                        if e_date.start.astimezone(local_tz) == schedule_datetime_start:
                            extra_slot = e_date
                            break

                    # Мехазм пропуска добавления диапазона в расписание
                    if extra_slot is not None:
                        #Также удаляем этот слот из массива экстрадат, чтобы не проверять его в последующих операциях
                        processed_extra_dates.remove(extra_slot)
                        filtered_processed_extra_dates.remove(extra_slot)

                        if extra_slot.type == 0:
                            #не добавляем слот если он с типом "не доступен для бронирования" в итоговой список
                            continue

                    schedule_datetime_end = datetime.combine(schedule_date, time(end_time, 0),
                                                             tzinfo=pytz.utc).astimezone(local_tz)

                    schedule_dates.append(
                        {
                            'start': schedule_datetime_start.strftime("%Y-%m-%d %H:%M"),
                            'end': schedule_datetime_end.strftime("%Y-%m-%d %H:%M")
                        }
                    )

            #Если в основном расписании день отмечен как нерабочий, но есть доп даты, то мы их отрисовываем

            # Все даты, которые остались, которые не пересекаются с текущим расписанием
            # либо с типом 0 (недоступно для бронирования), их не добавляем в итоговый список
            # либо с типом 1 (доступны для бронирования), добавляем в итоговоый список
            for extra_date in filtered_processed_extra_dates:
                if extra_date.type == 0:
                    continue

                schedule_datetime_start = extra_date.start.astimezone(local_tz)
                schedule_datetime_end = schedule_datetime_start + timedelta(hours=1)

                schedule_dates.append(
                    {
                        'start': schedule_datetime_start.strftime("%Y-%m-%d %H:%M"),
                        'end': schedule_datetime_end.strftime("%Y-%m-%d %H:%M")
                    }
                )

        return JsonResponse(
            {'data':
                {
                    'appointments': {
                        'as_expert': AppointmentSerializer(appointments_as_expert, many=True,
                                                           context={'request': request}).data,
                        'as_client': AppointmentSerializer(appointments_as_client, many=True,
                                                           context={'request': request}).data,
                    },
                    'extra_dates': ExpertScheduleSpecialDaysSerializer([], many=True,
                                                                       context={'request': request}).data,
                    'schedule': schedule_dates
                }
            })


@login_required
def get_clients_appointment(request, *args, **kwargs):
    appointments_as_client = Appointment.objects.filter(client=request.user)

    return JsonResponse(
        {'data':
            {
                'appointments': {
                    'as_client': AppointmentSerializer(appointments_as_client, many=True,
                                                       context={'request': request}).data,
                }
            }
        })
