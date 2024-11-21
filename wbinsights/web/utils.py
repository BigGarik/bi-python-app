import pytz
from datetime import datetime
from django.conf import settings
from urllib.parse import urljoin

from django.http import JsonResponse

from web.models import Profile
from web.services.timezone_translation import timezoneDictionary


def get_timezones(request):
    timezones = list(pytz.all_timezones)
    translated_timezones = []
    for tz in pytz.all_timezones:
        try:
            # Создаем объект часового пояса
            timezone = pytz.timezone(tz)

            # Получаем текущее время в этом часовом поясе
            now = datetime.now(timezone)

            # Форматируем смещение
            offset = now.strftime('%z')
            offset_str = f"{offset[:3]}:{offset[3:]}"

            # Добавляем оригинальное название в timezones
            timezones.append(tz)

            # Переводим название часового пояса на русский, если есть в словаре
            translated_name = timezoneDictionary.get(str(tz), tz)
            translated_timezone = f"{translated_name} {offset_str}"
            translated_timezones.append(translated_timezone)
        except Exception as e:
            # Пропускаем часовые пояса, которые вызывают ошибки
            pass
    return JsonResponse({'timezones': timezones, 'translated_timezones': translated_timezones})


def get_avatar_url(comment):
    """
    Возвращает URL аватара для данного комментария.

    :param comment: объект комментария, для которого нужно получить URL аватара.
    :return: строка с URL аватара.
    """
    if comment.user_id:
        profile = Profile.objects.filter(user=comment.user).first()
        if profile and profile.avatar:
            # Если у пользователя есть аватар, возвращаем его URL.
            return profile.avatar.url
        else:
            # Возвращаем URL аватара по умолчанию.
            return urljoin(settings.MEDIA_URL, 'avatars/profile_picture_icon.png')
    else:
        # Если у комментария нет связанного пользователя, возвращаем аватар по умолчанию.
        return urljoin(settings.MEDIA_URL, 'avatars/profile_picture_icon.png')

def is_mobile(context):
    request = context['request']
    return  is_mobile_by_request(request)

def is_mobile_by_request(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    mobile_agents = ['iphone', 'android', 'blackberry', 'windows phone', 'opera mini', 'mobile']
    return any(mobile_agent in user_agent for mobile_agent in mobile_agents)


if __name__ == '__main__':
    print(get_timezones(None))
