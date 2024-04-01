from django.contrib.auth.backends import ModelBackend, get_user_model
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q

from web.views.login import send_activation_email

UserModel = get_user_model()


class UserModelBackend(ModelBackend):
    """
    Переопределение авторизации
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:

            # if request.GET['login_by_phone']:
            #     user = UserModel.objects.get()
            user = UserModel.objects.get(Q(username=username) | Q(email__iexact=username))
        except UserModel.DoesNotExist:
            return None
        except MultipleObjectsReturned:
            return UserModel.objects.filter(email=username).order_by('id').first()
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                if not user.is_active:
                    # Пользователь найден, но не активен. Отправляем письмо с активацией.
                    send_activation_email(user, request)
                    # Если вы используете Django Messages
                    from django.contrib import messages
                    messages.info(request, 'Пожалуйста, проверьте свою почту для активации аккаунта.')
                return user

    def get_user(self, user_id):
        try:
            user = UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

        return user if self.user_can_authenticate(user) else None
