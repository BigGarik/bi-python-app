import pytz
from django.conf import settings
from urllib.parse import urljoin

from django.http import JsonResponse

from web.models import Profile


def get_timezones(request):
    timezones = list(pytz.all_timezones)
    return JsonResponse({'timezones': timezones})


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
