from datetime import datetime

from django.http import JsonResponse
from zoomus import ZoomClient

import os


def create_zoom_meeting(appointment):
    api_key = os.getenv('ZOOM_API_KEY')
    api_secret = os.getenv('ZOOM_API_SECRET')

    # Инициализация клиента Zoom
    client = ZoomClient(api_key, api_secret)

    # Данные для создания встречи
    topic = "Онлайн консультация"

    # Формат времени: ГГГГ-ММ-ДДTЧЧ:ММ:ССZ
    start_time = datetime.combine(appointment.appointment_date, appointment.appointment_time).strftime(
        '%Y-%m-%dT%H:%M:%SZ')

    # Продолжительность в минутах
    duration = 45

    # Список email адресов участников
    participants = [appointment.expert.email, appointment.client.email]

    # Создание встречи
    response = client.meeting.create(user_id='me', topic=topic, start_time=start_time, duration=duration,
                                     settings={'participants': participants})

    # Проверка успешности создания встречи
    if response.get('status') == 'success':
        meeting_id = response.get('id')
        join_url = response.get('join_url')
        return join_url
    # else:
    #     error_message = response.get('message', 'Failed to create meeting')
    #     return JsonResponse({'success': False, 'error': error_message})
