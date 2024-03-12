from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from web.models import CustomUser, Profile
from django import forms

from django.shortcuts import render, redirect
from django.contrib import messages

from web.models.users import ExpertProfile


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")


def profile_view(request):
    context = {
        "rating": 4.5,
        "experts_articles_count": 10,
        "experts_researches_count": 10,
        "experts_articles": [],
        "filled_stars_chipher": 'ffffh'

    }
    return render(request, "profile/profile.html", context=context)


class CustomUserChangeForm(forms.ModelForm):

    first_name = forms.CharField(label="Имя",
                                widget=forms.TextInput(
                                    attrs={'class': 'custom-form-css', 'placeholder': 'Введите имя'}))
    last_name = forms.CharField(label="Фамилия",
                               widget=forms.TextInput(
                                   attrs={'class': 'custom-form-css', 'placeholder': 'Введите фамилию'}))

    oldpassword = forms.CharField(label="Старый пароль", widget=forms.PasswordInput(attrs={'class': 'custom-form-css'}))
    newpassword = forms.CharField(label="Новый пароль", widget=forms.PasswordInput(attrs={'class': 'custom-form-css'}))
    confirmpassword = forms.CharField(label="Повторите новый пароль",
                                      widget=forms.PasswordInput(attrs={'class': 'custom-form-css'}))

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "oldpassword", "newpassword", "confirmpassword")  # photo


class ProfileChangeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("avatar",)


class ExpertProfileChangeForm(forms.ModelForm):
    about = forms.CharField(label="О себе",
                                    widget=forms.Textarea(
                                        attrs={'class': 'custom-aboutme-form', 'placeholder': 'Напишите текст о себе'}))
    education = forms.CharField(label="Образование", widget=forms.Textarea(attrs={'class': 'custom-education-form'}))
    age = forms.CharField(label="Возраст", widget=forms.Textarea(attrs={'class': 'custom-age-form'}))
    hour_cost = forms.CharField(label="Стоимость", widget=forms.Textarea(attrs={'class': 'custom-hourcost-form'}))
    category = forms.CharField(label="Категории экспертности",
                                    widget=forms.TextInput(attrs={'class': 'custom-form-css'}))
    experience = forms.IntegerField(label="Опыт работы (лет)",
                                    widget=forms.TextInput(attrs={'class': 'custom-form-css',
                                                                  'placeholder': 'Введите кол-во лет'}))

    class Meta:
        model = ExpertProfile
        fields = ("about", "education", "age", "hour_cost", "experience")  # photo


@login_required
def edit_user_profile(request):
    is_expert = False

    if request.user.profile.type == Profile.TypeUser.EXPERT:
        is_expert = True

    if request.method == 'POST':

        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        profile_form = ProfileChangeForm(request.POST, request.FILES, instance=request.user.profile)

        if is_expert:
            expert_profile_form = ExpertProfileChangeForm(request.POST, instance=request.user.expertprofile)

        if user_form.is_valid() and profile_form.is_valid() and (is_expert and expert_profile_form.is_valid()):

            user_form.save()
            profile_form.save()
            if is_expert:
                expert_profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='profile')
    else:
        user_form = CustomUserChangeForm(instance=request.user)
        profile_form = ProfileChangeForm(instance=request.user.profile)
        expert_profile_form = ExpertProfileChangeForm(instance=request.user.expertprofile)

    return render(request, 'profile/edit_profile.html',
                  {'user_form': user_form, 'profile_form': profile_form, "expert_profile_form": expert_profile_form})


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