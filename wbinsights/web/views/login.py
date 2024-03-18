from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.http import HttpResponse

from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect

from django import forms

from web.models import CustomUser, Profile
from web.models.users import ExpertProfile


# class CustomUserChangeForm(UserChangeForm):
#     class Meta:
#         model = CustomUser
#         fields = ("username", "email")

# Форма регистрации пользователя
class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(label="",choices=Profile.TypeUser, widget=forms.RadioSelect(attrs={'class': 'form-choose-user-type'})) #form-choose-user-type

    first_name = forms.CharField(label="Имя", widget=forms.TextInput(attrs={'class': 'form-inputs-custom'}))
    last_name = forms.CharField(label="Фамилия", widget=forms.TextInput(attrs={'class': 'form-inputs-custom'}))
    email = forms.CharField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-inputs-custom'}))
    # phone_number = forms.RegexField(label="телефон", widget=forms.TextInput(attrs={'class': '123'}), regex="^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$")
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'class': 'form-inputs-custom'}))
    password2 = forms.CharField(label="Повторите пароль", widget=forms.PasswordInput(attrs={'class': 'form-inputs-custom'}))

    # phone_number = forms.RegexField(regex="^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$")

    class Meta:
        model = CustomUser
        fields = ("user_type", "first_name", "last_name", "email", "password1", "password2")
        # fields = ("user_type", "username", "email", "phone_number", "password1", "password2")


class ExpertProfileForm(forms.ModelForm):

    about = forms.CharField(label="О себе", widget=forms.TextInput(attrs={'class': 'form-inputs-custom'}))
    experience = forms.CharField(label="Опыт", widget=forms.TextInput(attrs={'class': 'form-inputs-custom'}))
    hour_cost = forms.CharField(label="Стоимость", widget=forms.TextInput(attrs={'class': 'form-inputs-custom'}))


    class Meta:
        model = ExpertProfile
        fields = ("about", "experience", "hour_cost")


def signup_success(request):
    context = {
        "success_registration_message": "Поздравляем вы зарегистрированы"
    }
    return render(request, "registration/registration_success.html", context=context)


def gen_user_name_from_email(email):
    return email.replace("@", '_').replace(".", "_").replace("-", "_")


def register_user(request):
    if request.method == 'POST':

        user_form = CustomUserCreationForm(request.POST)

        if user_form.is_valid():

            new_username = gen_user_name_from_email(user_form.cleaned_data["email"])

            if user_form.cleaned_data["user_type"] and user_form.cleaned_data["user_type"] == '1':

                expert_profile_form = ExpertProfileForm(request.POST)

                if expert_profile_form.is_valid():
                    new_user = user_form.save(commit=False)
                    new_user.username = new_username
                    new_user.save()

                    new_user_profile = Profile()
                    new_user_profile.user = new_user
                    new_user_profile.type = Profile.TypeUser.EXPERT
                    new_user_profile.save()

                    new_expert_profile = expert_profile_form.save(commit=False)
                    new_expert_profile.user = new_user
                    new_expert_profile.save()

                    return redirect(to='signup_success', user_type=Profile.TypeUser.EXPERT)

            else:
                new_user = user_form.save(commit=False)
                new_user.username = new_username
                new_user.save()

                new_user_profile = Profile()
                new_user_profile.user = new_user
                new_user_profile.type = Profile.TypeUser.CLIENT
                new_user_profile.save()

                return redirect('signup_success')

    context = {
        "user_form": CustomUserCreationForm(),
        "expert_form": ExpertProfileForm()
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

    #     # form.user_type
    #     return super().form_valid(form)
