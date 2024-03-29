from datetime import datetime, timedelta

# from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
# from django.contrib.auth.views import LoginView
# from django.contrib import messages
from django.core.mail import send_mail
# from django.http import HttpResponse, request
from django.utils import timezone

from django.views.generic import CreateView
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect, get_object_or_404

from web.forms.users import CustomUserCreationForm, ExpertProfileForm, UserForgotPasswordForm, UserSetNewPasswordForm, \
    UserPasswordChangeForm
from web.models import Profile
from web.models.users import UserActivation


def signup_success(request):
    context = {
        "success_registration_message": "Поздравляем вы зарегистрированы. Для активации вашего аккаунта проверьте почту"
    }
    return render(request, "registration/registration_success.html", context=context)


def gen_user_name_from_email(email):
    return email.replace("@", '_').replace(".", "_").replace("-", "_")


def save_new_user_and_profile(request, user_form, user_type):
    new_username = gen_user_name_from_email(user_form.cleaned_data["email"])

    new_user = user_form.save(commit=False)
    new_user.username = new_username
    new_user.save()

    new_user_profile = Profile()
    new_user_profile.user = new_user
    new_user_profile.type = user_type
    new_user_profile.save()

    # Создаем ключ активации
    activation_key = default_token_generator.make_token(new_user)
    UserActivation.objects.create(user=new_user, activation_key=activation_key, expiration_date=timezone.now() + timedelta(days=1))

    # Отправляем письмо
    confirmation_link = request.build_absolute_uri(
        reverse('activate_account', kwargs={'activation_key': activation_key}))
    send_mail(
        'Подтверждение регистрации',
        f'Пожалуйста, перейдите по ссылке для активации аккаунта: {confirmation_link}',
        'info_dev@24wbinside.ru',
        [new_user.email],
        fail_silently=False,
    )

    return new_user


def register_user(request):
    expert_profile_form = None
    email_error = None

    if request.method == 'POST':

        user_form = CustomUserCreationForm(request.POST)

        if user_form.is_valid():
            if user_form.cleaned_data["user_type"] == '1':

                expert_profile_form = ExpertProfileForm(request.POST)
                if expert_profile_form.is_valid():
                    new_user = save_new_user_and_profile(request, user_form, Profile.TypeUser.EXPERT)
                    new_expert_profile = expert_profile_form.save(commit=False)
                    new_expert_profile.user = new_user
                    new_expert_profile.save()
                    return redirect(to='signup_success', user_type=Profile.TypeUser.EXPERT)
            else:

                save_new_user_and_profile(request, user_form, Profile.TypeUser.CLIENT)

                return redirect('signup_success')

        else:
            #check format
            if 'email' in user_form.errors:
                email_error = "Incorrect email format"
    else:
        user_form = CustomUserCreationForm()
        expert_profile_form = ExpertProfileForm()

    context = {
        "user_form": user_form,
        "expert_form": expert_profile_form,
        "email_error": email_error
    }

    return render(request, "registration/signup.html", context=context)


class WBIRegisterUser(CreateView):
    # create CustomUser

    # if (user_type == 'Expert')

    # we have to Create ExpertProfile
    # send email

    # else

    # send activation link

    # def form

    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

    # def form_valid(self, form: CustomUserCreationForm) -> HttpResponse:

# def custom_login(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         user = authenticate(request, email=email, password=password)
#         if user is not None:
#             login(request, user)
#             return redirect('home')
#         else:
#             error_message = "No account found with this email."
#             return render(request, 'registration/login.html', {'error_message': error_message})
#     return render(request, 'registration/login.html')


def activate_account(request, activation_key):
    user_activation = get_object_or_404(UserActivation, activation_key=activation_key)

    # Проверяем, не истек ли срок действия ключа
    if user_activation.has_expired():
        return render(request, 'registration/activation_expired.html')

    # Активация пользователя
    user = user_activation.user
    if default_token_generator.check_token(user, activation_key):
        user.is_active = True
        user.save()

        # Удаляем ключ активации из базы данных
        user_activation.delete()
        return render(request, 'registration/activation_complete.html')
    else:
        return render(request, 'registration/activation_invalid.html')


class UserPasswordChangeView(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("password_change_done")
    template_name = "registration/password_change_form.html"
    title = "Password change"


class UserForgotPasswordView(SuccessMessageMixin, PasswordResetView):
    """
    Представление по сбросу пароля по почте
    """
    form_class = UserForgotPasswordForm
    template_name = 'registration/password_reset_form.html'
    success_url = reverse_lazy('home')
    success_message = 'Письмо с инструкцией по восстановлению пароля отправлена на ваш email'
    subject_template_name = 'registration/email/password_reset_subject.txt'
    email_template_name = 'registration/email/password_reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Запрос на восстановление пароля'
        return context


class UserPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    """
    Представление установки нового пароля
    """
    form_class = UserSetNewPasswordForm
    template_name = 'system/user_password_set_new.html'
    success_url = reverse_lazy('home')
    success_message = 'Пароль успешно изменен. Можете авторизоваться на сайте.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Установить новый пароль'
        return context
