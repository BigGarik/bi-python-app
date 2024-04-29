from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from django_recaptcha.fields import ReCaptchaField

from ..models.users import Profile, CustomUser, ExpertProfile, Category


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name']


# Форма регистрации пользователя
class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(
        label="",
        initial=Profile.TypeUser.CLIENT,
        choices=Profile.TypeUser,
        widget=forms.RadioSelect(attrs={'class': 'form-choose-user-type'})
    )
    first_name = forms.CharField(label="Имя", widget=forms.TextInput(attrs={'class': 'form-inputs-custom'}))
    last_name = forms.CharField(label="Фамилия", widget=forms.TextInput(attrs={'class': 'form-inputs-custom'}))
    phone_number = forms.CharField(label="Телефон", widget=forms.TextInput(attrs={'class': 'form-inputs-custom'}))

    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-inputs-custom'}))
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'class': 'form-inputs-custom'}))
    password2 = forms.CharField(label="Повторите пароль",
                                widget=forms.PasswordInput(attrs={'class': 'form-inputs-custom'}))
    captcha = ReCaptchaField(label="Капча")

    class Meta:
        model = CustomUser
        fields = ("user_type", "first_name", "last_name", "phone_number", "email", "password1", "password2")

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')

        if first_name and last_name and first_name.lower() == last_name.lower():
            raise forms.ValidationError(_('Имя пользователя не может быть равно фамилии.'))

        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            try:
                validate_email(email)
            except ValidationError:
                raise ValidationError("Incorrect email format")

            if CustomUser.objects.filter(email=email).exists():
                raise ValidationError("Пользователь с таким email уже существует")
        return email


class ExpertProfileForm(forms.ModelForm):
    about = forms.CharField(label="О себе", widget=forms.Textarea(
        attrs={'class': 'form-inputs-custom', 'disabled': 'disabled', 'rows': 3}))
    experience = forms.DecimalField(label="Опыт", widget=forms.NumberInput(
        attrs={'class': 'form-inputs-custom', 'disabled': 'disabled'}))
    hour_cost = forms.DecimalField(label="Стоимость", widget=forms.NumberInput(
        attrs={'class': 'form-inputs-custom', 'disabled': 'disabled'}))

    categories = forms.ModelMultipleChoiceField(
        label="Категории экспертности",
        queryset=Category.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-inputs-custom'})  
    )

    class Meta:
        model = ExpertProfile
        fields = ("about", "experience", "hour_cost", "categories")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'type']


class UserPasswordChangeForm(PasswordChangeForm):
    """
        Форма изменения пароля
    """

    # class Meta:
    #     model = CustomUser
    #     fields = ['old_password', 'new_password1', 'new_password2']

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })


class UserProfilePasswordChangeForm(PasswordChangeForm):
    """
        Форма изменения пароля а странице профиля пользователя
    """

    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        required=False,
        widget=forms.PasswordInput(
            attrs={'class': 'custom-form-css'}
        ),
    )

    new_password1 = forms.CharField(
        label=_("New password"),
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'custom-form-css'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )

    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'custom-form-css'}),
    )


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(
            attrs={'class': 'form-control',
                   'placeholder': 'Введите Email',
                   'autocomplete': 'email'}
        )
    )


class UserSetNewPasswordForm(SetPasswordForm):
    error_messages = {
        "password_mismatch": "Пароли не совпадают"
    }
    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control',
                   'placeholder': 'Введите новый пароль',
                   "autocomplete": "new-password"}
        ),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label='Подтверждение нового пароля',
        strip=False,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control',
                   'placeholder': 'Подтвердите новый пароль',
                   "autocomplete": "new-password"}
        ),
    )


class VerifyExpertForm(forms.ModelForm):
    verify = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput())

    class Meta:
        model = ExpertProfile
        fields = ['verify']

    def save(self, *args, **kwargs):
        if self.cleaned_data['verify']:
            self.instance.is_verified = ExpertProfile.ExpertVerifiedStatus.VERIFIED
        self.instance.save()
