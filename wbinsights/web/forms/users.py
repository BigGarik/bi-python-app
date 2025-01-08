import logging
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.forms import modelformset_factory
from django.utils.translation import gettext_lazy as _
from django_recaptcha.fields import ReCaptchaField

from web.models.users import Profile, CustomUser, ExpertProfile, Category, Document, Education, ExpertAnketa, Grade

logger = logging.getLogger(__name__)

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name']


class CustomUserCreationForm(UserCreationForm):
    """ Форма регистрации пользователя """
    user_type = forms.ChoiceField(
        label="",
        initial=Profile.TypeUser.CLIENT,
        choices=Profile.TypeUser,
        widget=forms.RadioSelect(attrs={'class': 'form-choose-user-type'})
    )
    first_name = forms.CharField(label=_("First name"), widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label=_("Last name"), widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(label=_("Phone number"), widget=forms.TextInput(attrs={'class': 'form-control'}))

    email = forms.EmailField(label=_("Email"), widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label=_("Confirm password"),
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    #captcha = ReCaptchaField(label=_("Captcha"))

    class Meta:
        model = CustomUser
        fields = ("user_type", "first_name", "last_name", "phone_number", "email", "password1", "password2")

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')

        if first_name and last_name and first_name.lower() == last_name.lower():
            raise forms.ValidationError(_("The user's first name cannot be equal to the last name."))

        return cleaned_data

    def clean_phone_number(self):
        phone_number = super().clean()
        phone_number = phone_number.get('phone_number')

        if phone_number:
            # Проверяем, существует ли активированный пользователь с таким же номером телефона
            if CustomUser.objects.filter(phone_number=phone_number, is_active=True).exists():
                raise ValidationError(_("User with this phone number already exists and is active."))
        return phone_number

    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            try:
                validate_email(email)
            except ValidationError:
                raise ValidationError(_("Incorrect email format"))

            if CustomUser.objects.filter(email=email).exists():
                raise ValidationError(_("User with this email already exists."))
        return email


class ExpertAnketaForm(forms.ModelForm):
    about = forms.CharField(label=_("About me"), widget=forms.Textarea(
        attrs={'class': 'form-inputs-custom', 'disabled': 'disabled', 'rows': 3}))

    experience = forms.DecimalField(label=_("Experience"), widget=forms.NumberInput(
        attrs={'class': 'form-inputs-custom', 'disabled': 'disabled'}))

    hour_cost = forms.DecimalField(label=_("Price"), widget=forms.NumberInput(
        attrs={'class': 'form-inputs-custom', 'disabled': 'disabled'}))

    expert_categories = forms.ModelMultipleChoiceField(
        label=_("Categories of expertise"),
        queryset=Category.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-inputs-custom'})
    )

    class Meta:
        model = ExpertAnketa
        fields = ("about", "experience", "hour_cost", "expert_categories")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'type', 'timezone']


class UserPasswordChangeForm(PasswordChangeForm):
    """ Форма изменения пароля """
    def __init__(self, *args, **kwargs):
        """ Обновление стилей формы """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })


class UserProfilePasswordChangeForm(PasswordChangeForm):
    """ Форма изменения пароля на странице профиля пользователя """
    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        required=False,
        widget=forms.PasswordInput(
            attrs={
                    'class': 'custom-form-css',
                    'autocomplete': 'off',
                    }
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
        label=_("Confirm new password"),
        strip=False,
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'custom-form-css'}),
    )


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(
            attrs={'class': 'form-control',
                   'placeholder': 'Введите Email',
                   'autocomplete': 'email'}
        )
    )


class UserSetNewPasswordForm(SetPasswordForm):
    error_messages = {
        "password_mismatch": _("Password mismatch")
    }
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(
            attrs={'class': 'form-control',
                   'placeholder': _("Enter new password"),
                   "autocomplete": "new-password"}
        ),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("Confirm new password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control',
                   'placeholder': _("Confirm new password"),
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


def name_check(value):
    if len(value) < 2:
        raise forms.ValidationError('TESTING TESTING TESTING TESTING')


class CustomUserChangeForm(forms.ModelForm):
    first_name = forms.CharField(
        label="Имя",
        widget=forms.TextInput(attrs={'class': 'custom-form-css', 'placeholder': 'Введите имя'}),
        error_messages={'required': 'Пожалуйста, заполните это поле.'},
        validators=[name_check]
    )
    last_name = forms.CharField(
        label="Фамилия",
        widget=forms.TextInput(attrs={'class': 'custom-form-css', 'placeholder': 'Введите фамилию'}),
        error_messages={'required': 'Пожалуйста, заполните это поле.'},
        validators=[name_check]
    )

    oldpassword = forms.CharField(label="Старый пароль", required=False,
                                  widget=forms.PasswordInput(attrs={'class': 'custom-form-css'}))
    newpassword = forms.CharField(label="Новый пароль", required=False,
                                  widget=forms.PasswordInput(attrs={'class': 'custom-form-css'}))
    confirmpassword = forms.CharField(label="Повторите новый пароль", required=False,
                                      widget=forms.PasswordInput(attrs={'class': 'custom-form-css'}))

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')

        if first_name and len(first_name) == 0:
            self.add.error('first_name', 'THIS FIELD CANNOT BE EMPTY')

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name")


class ProfileChangeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("avatar",)
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'class': 'your-custom-class'}),
        }


class ExpertAnketaChangeForm(forms.ModelForm):
    about = forms.CharField(label=_("About me"), widget=forms.HiddenInput(
        attrs={'class': 'custom-aboutme-form', 'rows': 3, 'placeholder': 'Напишите текст о себе'}))
    age = forms.IntegerField(label=_("Age"), widget=forms.NumberInput(attrs={'class': 'custom-form-css'}))
    hour_cost = forms.IntegerField(label=_("Hourly rate"), widget=forms.NumberInput(attrs={'class': 'custom-form-css'}))
    expert_categories = forms.ModelMultipleChoiceField(
        label=_("Categories of expertise"),
        queryset=Category.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'custom-form-css'})
    )
    experience = forms.IntegerField(label=_("Experience (years)"), widget=forms.NumberInput(attrs={'class': 'custom-form-css'}))
    consulting_experience = forms.IntegerField(label=_("Consulting experience (years)"), required=False, widget=forms.NumberInput(attrs={'class': 'custom-form-css'}))
    hh_link = forms.URLField(label=_("Link to HeadHunter"), required=False, widget=forms.URLInput(attrs={'class': 'custom-form-css'}))
    linkedin_link = forms.URLField(label=_("Link to LinkedIn"), required=False, widget=forms.URLInput(attrs={'class': 'custom-form-css'}))
    experience_documents = forms.ModelMultipleChoiceField(
        label=_("Documents confirming experience"),
        queryset=Document.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'custom-form-css'}),
        required=False
    )

    class Meta:
        model = ExpertAnketa
        fields = ['about', 'age', 'hour_cost', 'expert_categories', 'experience', 'consulting_experience', 'hh_link', 'linkedin_link', 'experience_documents']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_hour_cost(self):
        hour_cost = self.cleaned_data.get("hour_cost")
        if self.user:
            try:
                expert_profile = ExpertProfile.objects.get(user=self.user)
                points = expert_profile.points
            except ExpertProfile.DoesNotExist:
                points = 0
        else:
            points = 0
        try:
            grade = Grade.objects.get(min_points__lte=points, max_points__gte=points)
            if not (grade.min_cost <= hour_cost <= grade.max_cost):
                self.add_error('hour_cost', f"Стоимость может быть между {grade.min_cost} и {grade.max_cost}.")
        except Grade.DoesNotExist:
            self.add_error('hour_cost', "No valid grade found for the given points.")

        return hour_cost


class EducationForm(forms.ModelForm):
    education_type = forms.ChoiceField(label=_("Type of education"), choices=Education.EDUCATION_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'custom-form-css'}))
    specialized_education = forms.BooleanField(label=_("Specialized education"), required=False, widget=forms.CheckboxInput(attrs={'class': 'custom-form-css'}))
    educational_institution = forms.CharField(label=_("Educational institution"), required=False, widget=forms.TextInput(attrs={'class': 'custom-form-css'}))
    # educational_institution_verified = forms.BooleanField(label=_("Institution verified"), required=False, widget=forms.CheckboxInput(attrs={'class': 'custom-form-css'}))
    diploma_number = forms.IntegerField(label=_("Diploma number"), required=False, widget=forms.NumberInput(attrs={'class': 'custom-form-css'}))
    # diploma_number_verified = forms.BooleanField(label=_("Diploma number verified"), required=False, widget=forms.CheckboxInput(attrs={'class': 'custom-form-css'}))
    degree_documents = forms.ModelMultipleChoiceField(
        label=_("Education documents"),
        queryset=Document.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'custom-form-css'}),
        required=False
    )

    class Meta:
        model = Education
        fields = ['education_type', 'specialized_education', 'educational_institution', 'diploma_number', 'degree_documents']


EducationFormSet = modelformset_factory(Education, form=EducationForm, extra=0)
