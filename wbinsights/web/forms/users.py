from django import forms
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from ..models.users import Profile, CustomUser, ExpertProfile


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name']


# Форма регистрации пользователя
class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(label="", initial=Profile.TypeUser.CLIENT,
                                  choices=Profile.TypeUser, widget=forms.RadioSelect(
                                    attrs={'class': 'form-choose-user-type'}))  # form-choose-user-type

    first_name = forms.CharField(label="Имя", widget=forms.TextInput(attrs={'class': 'form-inputs-custom'}))
    last_name = forms.CharField(label="Фамилия", widget=forms.TextInput(attrs={'class': 'form-inputs-custom'}))
    email = forms.CharField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-inputs-custom'}))
    # phone_number = forms.RegexField(label="телефон", widget=forms.TextInput(attrs={'class': '123'}),
                                     # regex="^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$")
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'class': 'form-inputs-custom'}))
    password2 = forms.CharField(label="Повторите пароль",
                                widget=forms.PasswordInput(attrs={'class': 'form-inputs-custom'}))

    # phone_number = forms.RegexField(regex="^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$")

    # agree_personal_data_policy = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class': '123'}))

    class Meta:
        model = CustomUser
        fields = ("user_type", "first_name", "last_name", "email", "password1", "password2")


class UserPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password1', 'new_password2']


class ExpertProfileForm(forms.ModelForm):
    about = forms.CharField(label="О себе",
                            widget=forms.Textarea(
                                attrs={'class': 'form-inputs-custom', 'disabled': 'disabled', 'rows': 3}))
    experience = forms.DecimalField(label="Опыт",
                                    widget=forms.NumberInput(
                                        attrs={'class': 'form-inputs-custom', 'disabled': 'disabled'}))
    hour_cost = forms.DecimalField(label="Стоимость",
                                   widget=forms.NumberInput(
                                       attrs={'class': 'form-inputs-custom', 'disabled': 'disabled'}))

    class Meta:
        model = ExpertProfile
        fields = ("about", "experience", "hour_cost")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'type']
