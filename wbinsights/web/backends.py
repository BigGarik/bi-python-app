from django.contrib.auth.backends import ModelBackend, get_user_model
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q
from django.contrib import messages
from web.views.user import send_activation_email
from django.utils.translation import gettext_lazy as _

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
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
            else:
                if not user.is_active:
                    messages.info(request, _('Please check your email to activate your account.'))
                    # Пользователь найден, но не активен. Отправляем письмо с активацией.
                    send_activation_email(user, request)
        except UserModel.DoesNotExist:
            return None
        except MultipleObjectsReturned:
            return UserModel.objects.filter(email=username).order_by('id').first()

    def get_user(self, user_id):
        try:
            user = UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

        return user if self.user_can_authenticate(user) else None
