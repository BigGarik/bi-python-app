import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordChangeView, LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from web.forms.users import CustomUserCreationForm, ExpertAnketaForm, UserPasswordResetForm, UserSetNewPasswordForm, \
    UserPasswordChangeForm
from web.models import Profile
from django.db import transaction
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger('django-debug')

User = get_user_model()


def signup_success(request):
    context = {
        "success_registration_message": "Поздравляем вы зарегистрированы. Для активации вашего аккаунта проверьте почту"
    }
    return render(request, "registration/registration_success.html", context=context)


def gen_user_name_from_email(email):
    return email.replace("@", '_').replace(".", "_").replace("-", "_")


# При создании пользователя после заполнения формы регистрации
def send_activation_email(user, request):
    signer = TimestampSigner()
    token = signer.sign(user.pk)
    confirmation_link = request.build_absolute_uri(reverse('activate_account', kwargs={'token': token}))

    html_content = render_to_string('emails/account_activation.html', {'confirmation_link': confirmation_link})
    # Получаем текстовую версию письма из HTML
    text_content = strip_tags(html_content)

    # Создаем объект EmailMultiAlternatives
    email = EmailMultiAlternatives(
        'Активация аккаунта',
        text_content,
        'info_dev@24wbinside.ru',
        [user.email]
    )
    # Добавляем HTML версию
    email.attach_alternative(html_content, "text/html")
    email.send()


def resend_activation_email(request, email):
    email = request.POST.get('email')
    try:
        user = User.objects.get(email=email)
        if not user.is_active:
            send_activation_email(user, request)
            return redirect('activation_email_resent')
    except ObjectDoesNotExist:
        # Пользователь не найден. Информируйте пользователя, что аккаунт не был найден и предложите зарегистрироваться
        return render(request, 'account_not_found.html', {'email': email})


def save_new_user_and_profile(request, user_form, user_type):
    new_username = gen_user_name_from_email(user_form.cleaned_data["email"])
    try:
        new_user = user_form.save(commit=False)
        new_user.username = new_username
        new_user.save()

        new_user_profile = Profile()
        new_user_profile.user = new_user
        new_user_profile.type = user_type
        new_user_profile.save()
    except Exception as e:
        logger.error(f"Error creating new user: {e}")
    try:
        send_activation_email(new_user, request)
    except Exception as e:
        logger.error(f"Error sending activation email: {e}")
    logger.debug(f"New user created:  {new_user}")

    return new_user


@transaction.atomic
def register_user(request):
    def is_mobile(request):
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        return 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent

    def get_template_name(request):
        return 'registration/signup_mobile.html' if is_mobile(request) else 'registration/signup.html'

    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        if user_form.data['user_type'] == '1':  # Expert
            expert_profile_form = ExpertAnketaForm(request.POST)
            if user_form.is_valid() and expert_profile_form.is_valid():
                try:
                    new_user = save_new_user_and_profile(request, user_form, Profile.TypeUser.EXPERT)
                    new_expert_profile = expert_profile_form.save(commit=False)
                    new_expert_profile.user = new_user
                    new_expert_profile.save()
                    expert_profile_form.save_m2m()
                    return redirect('signup_success')
                except Exception as e:
                    logger.error(f"Error during expert registration: {str(e)}", exc_info=True)
                    messages.error(request, _("An error occurred during registration. Please try again."))
            else:
                logger.debug(
                    f"Invalid form data: user_form errors: {user_form.errors}, expert_form errors: {expert_profile_form.errors}")
                context = {
                    "user_form": user_form,
                    "expert_form": expert_profile_form,
                    "is_mobile": is_mobile(request)
                }
                return render(request, get_template_name(request), context=context)
        if user_form.data['user_type'] == '0':
            if user_form.is_valid():
                save_new_user_and_profile(request, user_form, Profile.TypeUser.CLIENT)
                return redirect('signup_success')
            else:
                context = {
                    "user_form": user_form,
                    "is_mobile": is_mobile(request)
                }
                return render(request, get_template_name(request), context=context)
    if request.method == 'GET':
        context = {
            "user_form": CustomUserCreationForm(),
            "expert_form": ExpertAnketaForm(),
            "is_mobile": is_mobile(request)
        }
        return render(request, get_template_name(request), context=context)

def activate_account(request, token):
    signer = TimestampSigner()
    try:
        # проверяем возраст токена, его действие ограничено 48 часами (3600 * 48 секунд)
        user_id = signer.unsign(token, max_age=3600 * 48)
        user = User.objects.get(pk=user_id)
        if not user.is_active:
            user.is_active = True
            user.save()
            # Перенаправление на страницу успешной активации
            return render(request, 'registration/activation_complete.html')
        else:
            messages.info(request, _("Your account is already activated."))
            return redirect('login')
    except SignatureExpired:
        # Срок действия токена истек, предложить отправить ключ активации повторно
        user_id = signer.unsign(token, max_age=None)
        user = User.objects.get(pk=user_id)
        return render(request, 'registration/activation_expired.html', {'email': user.email})
    except BadSignature:
        messages.error(request, _("Activation link is invalid."))
        return redirect('login')
    except User.DoesNotExist:
        messages.error(request, _("Account activation error: user not found."))
        return redirect('signup')
    # else:
    #     return render(request, 'registration/activation_invalid.html')


# class UserPasswordChangeView(PasswordChangeView):
#     form_class = UserPasswordChangeForm
#     success_url = reverse_lazy("password_change_done")
#     template_name = "registration/password_change_form.html"
#     title = "Password change"


class UserPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("index")
    template_name = "registration/password_change_form.html"
    title = "Password change"
    success_message = "Password changed successfully."

    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            form = self.get_form()
            context = self.get_context_data(form=form)
            html = render_to_string(self.template_name, context, request=request)
            return JsonResponse({'html': html})
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # print("POST data:", request.POST) # Отладочное сообщение
        form = self.get_form()
        if form.is_valid():
            form.save()
            messages.success(request, self.success_message)
            # return JsonResponse({'success': True, 'message': self.success_message, 'redirect_url': str(self.success_url)})
            return redirect(self.get_success_url())
        else:
            context = self.get_context_data(form=form)
            html = render_to_string(self.template_name, context, request=request)
            return JsonResponse({'success': False, 'html': html})


class UserPasswordResetView(SuccessMessageMixin, PasswordResetView):
    """
    Представление по сбросу пароля по почте
    """
    form_class = UserPasswordResetForm
    template_name = 'registration/password_reset_form.html'
    success_url = reverse_lazy('password_reset_done')
    success_message = 'Письмо с инструкцией по восстановлению пароля отправлена на ваш email'
    subject_template_name = 'registration/email/password_reset_subject.txt'
    email_template_name = 'registration/email/password_reset_email.html'


class UserPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    """
    Представление установки нового пароля
    """
    form_class = UserSetNewPasswordForm
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')
    success_message = 'Пароль успешно изменен. Можете авторизоваться на сайте.'


class CustomLoginView(LoginView):

    def get_template_names(self):
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
            return ['registration/login_mobile.html']
        else:
            return ['registration/login.html']
