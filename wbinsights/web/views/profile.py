from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags

from wbappointment.forms import ExpertScheduleForm
from wbappointment.models import Appointment
from wbinsights.settings import SERVER_EMAIL
from web.forms.users import UserProfilePasswordChangeForm, ExpertProfileChangeForm, CustomUserChangeForm, \
    ProfileChangeForm, EducationFormSet
from web.models import CustomUser, Profile
from django.utils.translation import gettext_lazy as _

from django.shortcuts import render, redirect
from django.contrib import messages

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
                    expert_id = request.user.pk
                    # Получаем список email-адресов всех модераторов
                    moderators = CustomUser.objects.filter(is_staff=True)
                    recipient_list = [moderator.email for moderator in moderators if moderator.email]
                    manage_unverified_experts_profile = request.build_absolute_uri(
                                                        reverse("manage_unverified_experts_profile",
                                                                kwargs={"pk": expert_id}))
                    manage_unverified_experts_list = request.build_absolute_uri(reverse("manage_unverified_experts_list"))

                    html_content = render_to_string('emails/verification_email.html',
                                                    {'manage_unverified_experts_profile': manage_unverified_experts_profile,
                                                     'manage_unverified_experts_list': manage_unverified_experts_list})
                    text_content = strip_tags(html_content)

                    # Создаем объект EmailMultiAlternatives
                    email = EmailMultiAlternatives(
                        'Новая анкета эксперта на проверку',
                        text_content,
                        SERVER_EMAIL,
                        recipient_list
                    )
                    # Добавляем HTML версию
                    email.attach_alternative(html_content, "text/html")
                    email.send()

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
            expert_articles = Article.objects.filter(author=request.user)
            expert_articles_count = Article.objects.filter(author=request.user).count()

            experts_appointment_cnt = Appointment.objects.filter(expert=request.user).count()

            # Update the context with expert-specific data
            context.update({
                "experts_articles": expert_articles,
                "experts_articles_count": expert_articles_count,
                "rating": 4.5,
                "experts_researches_count": 0,
                "filled_stars_chipher": 'ffffh',
                "users_appointment_cnt": experts_appointment_cnt,
                "appointment_title": "Онлайн консультация",
                "user_type": Profile.TypeUser.EXPERT

            })

    else:
        # For non-expert users, render the client profile template
        profile_template = "profile/client/profile.html"
        # clients_appointment = Appointment.objects.filter(client=request.user)
        clients_appointment_cnt = Appointment.objects.filter(client=request.user).count()
        context.update({
            "users_appointment_cnt": clients_appointment_cnt,
            "experts_articles": [],
            "experts_articles_count": 0,
            "experts_researches_count": 0,
            "user_type": Profile.TypeUser.CLIENT
        })

    return render(request, profile_template, context=context)


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
        education_expert_formset = EducationFormSet(queryset=request.user.expertprofile.educations.all())

    context = {}

    if request.method == 'POST':

        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        profile_form = ProfileChangeForm(request.POST, request.FILES, instance=request.user.profile)
        user_change_password_form = UserProfilePasswordChangeForm(user=request.user, data=request.POST)

        if is_expert:
            expert_profile_form = ExpertProfileChangeForm(request.POST, instance=request.user.expertprofile)
            education_expert_formset = EducationFormSet(request.POST, queryset=request.user.expertprofile.educations.all())

        saveNewPassword = False
        if user_change_password_form.data['old_password'] and user_change_password_form.data['old_password'] != '':
            saveNewPassword = True

        if (user_form.is_valid() and profile_form.is_valid()
                and (not is_expert or expert_profile_form.is_valid())
                and (not is_expert or education_expert_formset.is_valid())
                and (not saveNewPassword or user_change_password_form.is_valid())):
            user_form.save()
            profile_form.save()

            if is_expert:
                expert_profile_form.save()
                # Сохраняем каждую форму в формсете
                educations = education_expert_formset.save(commit=False)
                for education in educations:
                    education.expert_profile = request.user.expertprofile
                    education.save()

            if saveNewPassword:
                user_change_password_form.save()
                # переавторизовываем пользователя с новым паролем
                update_session_auth_hash(request, request.user)

            messages.success(request, _('Your profile is updated successfully'))
            return redirect('profile')

    #  user_change_password_form
    context.update({
        'user_form': user_form,
        'profile_form': profile_form,
        'user_change_password_form': user_change_password_form
    })

    if is_expert:
        context.update({
            "expert_profile_form": expert_profile_form,
            "education_expert_formset": education_expert_formset,
        })

    return render(request, profile_edit_template, context=context)
