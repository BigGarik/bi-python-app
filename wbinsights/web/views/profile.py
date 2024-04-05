from django.contrib.auth.decorators import login_required

from web.forms.users import UserProfilePasswordChangeForm
from web.models import CustomUser, Profile
from django import forms

from django.shortcuts import render, redirect
from django.contrib import messages

from web.models.users import ExpertProfile
from web.models import Article

from django.contrib.auth import update_session_auth_hash

@login_required
def profile_view(request):
    # Check if the user is an expert
    is_expert = request.user.profile.type == Profile.TypeUser.EXPERT

    # Initialize the context with common data
    context = {}
    profile_template = "profile/expert/profile.html"

    if is_expert:
        if not request.user.expertprofile.is_verified:
            # If expert profile is not verified, render the anketa template
            if request.method == 'POST':
                expert_profile_form = ExpertProfileChangeForm(request.POST, instance=request.user.expertprofile)
                if expert_profile_form.is_valid():
                    expert_profile_form.save()
                    messages.success(request, 'Your profile has successfully been sent for verification')
                    return redirect('index')
            else:
                expert_profile_form = ExpertProfileChangeForm(instance=request.user.expertprofile)

            profile_template = 'profile/anketa.html'
            context.update({
                "expert_profile_form": expert_profile_form,
                "experts_articles": [],
                "rating": 4.5,
                "experts_articles_count": 0,
                "experts_researches_count": 0,
                "filled_stars_chipher": 'ffffh'
            })
        else:
            # Fetch the expert's articles if profile is verified
            expert_articles = Article.objects.filter(author=request.user)[:7]
            expert_articles_count = Article.objects.filter(author=request.user).count()
            # Update the context with expert-specific data
            context.update({
                "experts_articles": expert_articles,
                "rating": 4.5,
                "experts_articles_count": expert_articles_count,
                "experts_researches_count": 0,
                "filled_stars_chipher": 'ffffh'
            })

    else:
        # For non-expert users, render the client profile template
        profile_template = "profile/client/profile.html"
        context.update({
            "experts_articles": [],
            "experts_articles_count": 0,
            "experts_researches_count": 0,
        })

    return render(request, profile_template, context=context)


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

    oldpassword = forms.CharField(label="Старый пароль", required=False, widget=forms.PasswordInput(attrs={'class': 'custom-form-css'}))
    newpassword = forms.CharField(label="Новый пароль", required=False, widget=forms.PasswordInput(attrs={'class': 'custom-form-css'}))
    confirmpassword = forms.CharField(label="Повторите новый пароль", required=False,
                                      widget=forms.PasswordInput(attrs={'class': 'custom-form-css'}))

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')

        if first_name and len(first_name) == 0:
            self.add.error('first_name', 'THIS FIELD CANNOT BE EMPTY')

    def clean(self):
        cleaned_data = super().clean()
        last_name = cleaned_data.get('last_name')

        if last_name and len(last_name) == 0:
            self.add.error('last_name', 'THIS FIELD ALSO CANNOT BE EMPTY')

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name")  # photo

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     for field_name, field in self.fields.items():
    #         field.error_messages = {'required': 'This field cannot be empty.'}


# class MessageForm(forms.Form):
#     text_input = forms.CharField(
#         error_messages={'required': 'This is a custom error message for #862'}
#     )

#     helper = FormHelper()
#     helper.layout = Layout(
#         Field('text_input', css_class='form-control-lg'),

#     )


class ProfileChangeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("avatar",)
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'class': 'your-custom-class'}),
        }


class ExpertProfileChangeForm(forms.ModelForm):
    about = forms.CharField(label="О себе", widget=forms.Textarea(
        attrs={'class': 'custom-aboutme-form', 'placeholder': 'Напишите текст о себе'}))
    education = forms.CharField(label="Образование", widget=forms.TextInput(attrs={'class': 'custom-form-css'}))
    age = forms.CharField(label="Возраст", widget=forms.TextInput(attrs={'class': 'custom-form-css'}))
    hour_cost = forms.CharField(label="Стоимость", widget=forms.TextInput(attrs={'class': 'custom-form-css'}))
    category = forms.CharField(label="Категории экспертности",
                               widget=forms.TextInput(attrs={'class': 'custom-form-css'}))
    experience = forms.IntegerField(label="Опыт работы (лет)", widget=forms.TextInput(
        attrs={'class': 'custom-form-css', 'placeholder': 'Введите кол-во лет'}))

    class Meta:
        model = ExpertProfile
        fields = ("about", "education", "age", "hour_cost", "experience")  # photo


@login_required
def edit_user_profile(request):

    is_expert = request.user.profile.type == Profile.TypeUser.EXPERT

    profile_edit_template = 'profile/expert/edit_profile.html'

    if not is_expert:
        profile_edit_template = 'profile/client/edit_profile.html'

    user_form = CustomUserChangeForm(instance=request.user)
    profile_form = ProfileChangeForm(instance=request.user.profile)
    user_change_password_form = UserProfilePasswordChangeForm(user=request.user)

    if is_expert:
        expert_profile_form = ExpertProfileChangeForm(instance=request.user.expertprofile)

    context = {}

    if request.method == 'POST':

        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        profile_form = ProfileChangeForm(request.POST, request.FILES, instance=request.user.profile)
        user_change_password_form = UserProfilePasswordChangeForm(user=request.user, data=request.POST)

        if is_expert:
            expert_profile_form = ExpertProfileChangeForm(request.POST, instance=request.user.expertprofile)

        saveNewPassword = False
        if user_change_password_form.data['old_password'] and user_change_password_form.data['old_password'] != '':
            saveNewPassword = True

        if (user_form.is_valid() and profile_form.is_valid()
                and (not is_expert or expert_profile_form.is_valid())
                and (not saveNewPassword or user_change_password_form.is_valid())):
            user_form.save()
            profile_form.save()

            if is_expert:
                expert_profile_form.save()

            if saveNewPassword:
                user_change_password_form.save()
                #переавторизовываем пользователя с новым паролем
                update_session_auth_hash(request, request.user)

            messages.success(request, 'Your profile is updated successfully')
            return redirect('profile')

    #  user_change_password_form
    context.update({
        'user_form': user_form,
        'profile_form': profile_form,
        'user_change_password_form': user_change_password_form
    })

    if is_expert:
        context.update({
            "expert_profile_form": expert_profile_form
        })

    return render(request, profile_edit_template, context=context)

# class ProfileUpdateView(UpdateView):
#     model = CustomUser
#     form_class = CustomUserForm
#     second_form_class = ProfileForm
#     template_name = 'posts/users/edit_profile.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         if 'form2' not in context:
#             context['form2'] = self.second_form_class
#         return context

#     def get_object(self, queryset=None):
#         return self.request.user

#     def form_valid(self, form):
#         form2 = self.second_form_class(self.request.POST, self.request.FILES, instance=self.request.user.profile)

#         if form2.is_valid():
#             form2.save()
#             return super().form_valid(form)
#         else:
#             return self.render_to_response(self.get_context_data(form=form, form2=form2))

#     def get_success_url(self):
#         return reverse('user_profile', kwargs={'pk': self.request.user.pk})
