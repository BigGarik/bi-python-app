from datetime import datetime

from django.http import JsonResponse
from zoomus import ZoomClient

import os


def create_zoom_meeting(appointment):

    zoom_api_key = os.getenv('ZOOM_API_KEY')
    zoom_api_secret = os.getenv('ZOOM_API_SECRET')
    zoom_api_account_id = os.getenv('ZOOM_ACCOUNT_ID')

    # Инициализация клиента Zoom
    client = ZoomClient(zoom_api_key, zoom_api_secret, api_account_id=zoom_api_account_id)

    # Данные для создания встречи
    topic = "Онлайн консультация"

    # Формат времени: ГГГГ-ММ-ДДTЧЧ:ММ:ССZ
    start_time = appointment.appointment_datetime

    # Продолжительность в минутах
    duration = 45

    # Список email адресов участников
    participants = [appointment.expert.email, appointment.client.email]



    # Создание встречи
    response = client.meeting.create(user_id='me',
                                     topic=topic, start_time=start_time, duration=duration,
                                     type=2, timezone=appointment.expert.profile.timezone,
                                     settings={'participants': participants,
                                               'waiting_room': False,
                                               'join_before_host': True,
                                               'approval_type': 0}
                                     )

    # Проверка успешности создания встречи
    if response.ok:
        data = response.json()
        meeting_id = data.get('id')
        join_url = data.get('join_url')
        return join_url
    # else:
    #     error_message = response.get('message', 'Failed to create meeting')
    #     return JsonResponse({'success': False, 'error': error_message})
