from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.forms import modelformset_factory
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags

from web.models import RatingCalculate, RatingRole
from web.models.users import Education, ExpertAnketa, ExpertProfile
from wbappointment.models import Appointment
from wbinsights.settings import SERVER_EMAIL
from web.forms.users import UserProfilePasswordChangeForm, ExpertAnketaChangeForm, CustomUserChangeForm, \
    ProfileChangeForm, EducationForm
from web.models import CustomUser, Profile
from django.utils.translation import gettext_lazy as _

from django.shortcuts import render, redirect
from django.contrib import messages

from web.models import Article

from expertprojects.views import GetProjectsView
from expertprojects.models import UserProject

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#
# @login_required
# def anketa_view(request):
#     if not request.user.profile.type == Profile.TypeUser.EXPERT:  # or request.user.expertprofile.is_verified:
#         # Если пользователь не эксперт или его анкета уже верифицирована, перенаправляем на главную страницу
#         return redirect('index')
#
#     if request.method == 'POST':
#         expert_profile_form = ExpertAnketaChangeForm(request.POST, instance=request.user.expertprofile)
#         if expert_profile_form.is_valid():
#             # Сохраняем форму и отправляем уведомление модераторам
#             expert_profile_form.save()
#             expert_id = request.user.pk
#             # Получаем список email-адресов всех модераторов
#             moderators = CustomUser.objects.filter(is_staff=True)
#             recipient_list = [moderator.email for moderator in moderators if moderator.email]
#             manage_unverified_experts_profile = request.build_absolute_uri(
#                 reverse("manage_unverified_experts_profile",
#                         kwargs={"pk": expert_id}))
#             manage_unverified_experts_list = request.build_absolute_uri(reverse("manage_unverified_experts_list"))
#
#             html_content = render_to_string('emails/verification_email.html',
#                                             {'manage_unverified_experts_profile': manage_unverified_experts_profile,
#                                              'manage_unverified_experts_list': manage_unverified_experts_list})
#             text_content = strip_tags(html_content)
#
#             # Создаем объект EmailMultiAlternatives
#             email = EmailMultiAlternatives(
#                 'Новая анкета эксперта на проверку',
#                 text_content,
#                 SERVER_EMAIL,
#                 recipient_list
#             )
#             # Добавляем HTML версию
#             email.attach_alternative(html_content, "text/html")
#             email.send()
#             messages.success(request, _('Your profile has successfully been sent for verification'))
#             return redirect('index')
#     else:
#         expert_profile_form = ExpertAnketaChangeForm(instance=request.user.expertprofile)
#
#     context = {
#         "expert_profile_form": expert_profile_form,
#         "experts_articles": [],
#         "rating": 4.5,
#         "experts_articles_count": 0,
#         "experts_researches_count": 0,
#         "filled_stars_chipher": 'ffffh'
#     }
#
#     return render(request, 'profile/anketa.html', context)


# class ProfileView(DetailView):
#     model = CustomUser

@login_required
def profile_view(request):
    # Check if the user is an expert
    is_expert = request.user.profile.type == Profile.TypeUser.EXPERT

    # context = {'tab': tab}

    # Remove 'category' from the GET parameters
    get_params = request.GET.copy()
    if 'category' in get_params:
        del get_params['category']

    # Initialize the context with common data
    context = {'get_params': get_params}
    profile_template = "profile/expert/profile.html"

    if is_expert:

        try:

            expert_profile = request.user.expertanketa

        except Exception as e:

            expertAnketa = ExpertAnketa()
            expertAnketa.user = request.user
            expertAnketa.save()

            expert_profile = request.user.expertanketa

        # Fetch the expert's articles if profile is verified
        expert_articles = Article.objects.filter(author=request.user)
        expert_articles_count = Article.objects.filter(author=request.user).count()
        experts_appointment_cnt = Appointment.objects.filter(expert=request.user).count()
        projects_count = UserProject.objects.filter(author=request.user).count()

        # Fetch the expert's projects
        projects_view = GetProjectsView()
        projects_view.request = request
        queryset = projects_view.get_queryset()
        page_size = projects_view.get_paginate_by(queryset)
        paginator = Paginator(queryset, page_size)
        page = request.GET.get('page', 1)

        try:
            projects = paginator.page(page)
        except PageNotAnInteger:
            projects = paginator.page(1)
        except EmptyPage:
            projects = paginator.page(paginator.num_pages)


        # Fetch ratings and roles
        ratings = RatingCalculate.objects.select_related('role').filter(user=request.user)
        roles = RatingRole.objects.all()
        rating = ExpertProfile.objects.filter(user=request.user).first()

        # Update the context with expert-specific data
        context.update({
            "experts_articles": expert_articles,
            "experts_articles_count": expert_articles_count,
            "rating": rating,
            "experts_researches_count": 0,
            "filled_stars_chipher": 'ffffh',
            "users_appointment_cnt": experts_appointment_cnt,
            "appointment_title": "Онлайн консультация",
            "user_type": Profile.TypeUser.EXPERT,
            "projects": projects,
            "projects_count": projects_count,
            "user": request.user,
            "profile": expert_profile,
            "ratings": ratings,
            "roles": roles
        })
    else:
        # For non-expert users, render the client profile template
        profile_template = "profile/client/profile.html"
        clients_appointment_cnt = Appointment.objects.filter(client=request.user).count()
        context.update({
            "users_appointment_cnt": clients_appointment_cnt,
            "experts_articles": [],
            "experts_articles_count": 0,
            "experts_researches_count": 0,
            "user_type": Profile.TypeUser.CLIENT
        })

    return render(request, profile_template, context=context)

# class ClientProfileEditHandler:
#
#     def __init__(self, request):
#         self.user_form = CustomUserChangeForm(request.POST, instance=request.user)
#         self.profile_form = ProfileChangeForm(request.POST, request.FILES, instance=request.user.profile)
#
#     def save_profile(self):
#         if self.user_form.is_valid() and self.profile_form.is_valid():
#             self.user_form.save()
#             self.profile_form.save()
#
#     def get_template(self):
#         return 'profile/client/edit_profile.html'


# class ExpertProfileEditHandler:
#
#     def save_anketa(self, request):
#
#         user_form = CustomUserChangeForm(request.POST, instance=request.user)
#         expert_anketa_form = ExpertAnketaChangeForm(request.POST, instance=request.user.expertanketa)
#         educationFormSet_0 = modelformset_factory(Education, form=EducationForm, exclude=[], extra=0)
#         education_expert_anketa_formset = educationFormSet_0(request.POST, queryset=request.user.expertanketa.education.all())
#
#         if user_form.is_valid() and expert_anketa_form.is_valid() and education_expert_anketa_formset.is_valid():
#
#             user_form.save()
#
#             updated_expert_anketa: ExpertAnketa = expert_anketa_form.save(commit=False)
#             updated_expert_anketa.is_verified = ExpertAnketa.AnketaVerifiedStatus.NOT_VERIFIED
#             updated_expert_anketa.save()
#
#             for cat in updated_expert_anketa.expert_categories.all():
#                 print(cat.slug)
#
#             educations = education_expert_anketa_formset.save(commit=False)
#             for education in educations:
#                 education.save()
#
#     def is_valid(self):
#         return (self.user_form.is_valid()
#                 and self.expert_anketa_form.is_valid()
#                 and self.education_expert_anketa_formset.is_valid())
#
#     def get_form_errors(self):
#         return {
#             'errors': {
#                 'user_form': self.user_form.errors,
#                 'expert_anketa_form': self.expert_anketa_form.errors,
#                 'education_expert_formset': self.education_expert_anketa_formset.errors
#             }
#         }


@login_required
def edit_user_profile(request):
    is_expert = request.user.profile.type == Profile.TypeUser.EXPERT

    profile_edit_template = 'profile/client/edit_profile.html'

    if is_expert:
        profile_edit_template = 'profile/expert/edit_profile.html'

    if request.method == 'GET':

        user_form = CustomUserChangeForm(instance=request.user)
        profile_form = ProfileChangeForm(instance=request.user.profile)
       # user_change_password_form = UserProfilePasswordChangeForm(user=request.user)

        if is_expert:
            """ Анкета """

            # user_form = CustomUserChangeForm(instance=request.user)
            expert_profile_form = ExpertAnketaChangeForm(instance=request.user.expertanketa)

            user_education = request.user.expertanketa.education
            if user_education.exists():
                education_expert_formset_factory = modelformset_factory(Education, form=EducationForm, exclude=[],
                                                                        extra=0)
                education_expert_formset = education_expert_formset_factory(queryset=user_education.all())
            else:
                education_expert_formset_factory = modelformset_factory(Education, form=EducationForm, extra=1)
                education_expert_formset = education_expert_formset_factory(queryset=Education.objects.none())

        context = {
            'user_form': user_form,
            'profile_form': profile_form,
        }

        if is_expert:
            context.update({
                "expert_profile_form": expert_profile_form,
                "education_expert_formset": education_expert_formset,
            })

        return render(request, profile_edit_template, context=context)

    if request.method == 'POST':

        if is_expert:

            # Эксперт может сохранить свои данные только в виде анкеты
            # В профиль эти данные сохранит менеджер при аппруве анкеты

            user_form = CustomUserChangeForm(request.POST, instance=request.user)
            expert_anketa_form = ExpertAnketaChangeForm(request.POST, instance=request.user.expertanketa)
            educationFormSet = modelformset_factory(Education, form=EducationForm, exclude=[], extra=0)
            education_expert_anketa_formset = educationFormSet(request.POST,
                                                                 queryset=request.user.expertanketa.education.all())

            if user_form.is_valid() and expert_anketa_form.is_valid() and education_expert_anketa_formset.is_valid():

                user_form.save()

                #Здесь мы не можем сделать save(commit=False) потому что сущности еще может не быть и мы
                #по сути можем сделать ссылку на несуществующую сущность, поэтому django не сохраняет manyTomany
                #методом save(commit=False)
                updated_expert_anketa: ExpertAnketa = expert_anketa_form.save()

                for form in education_expert_anketa_formset.forms:
                    #EducationForm
                    education = form.save()
                    education.expert = request.user
                    education.save()
                    updated_expert_anketa.education.add(education)

                updated_expert_anketa.is_verified = ExpertAnketa.AnketaVerifiedStatus.NOT_VERIFIED
                updated_expert_anketa.save()


                #Отправляем письмо модераторам, о необходимости проверки анкеты
                moderators = CustomUser.objects.filter(is_staff=True)
                recipient_list = [moderator.email for moderator in moderators if moderator.email]
                manage_unverified_experts_profile = request.build_absolute_uri(
                    reverse("manage_unverified_experts_profile",
                            kwargs={"pk": request.user.id }))
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
                ############################

                messages.success(request, _('Your profile has successfully been sent for verification'))
                redirect('profile')

            else:

                context = {
                    "user_form": user_form,
                    "profile_form": expert_anketa_form,
                    "expert_profile_form": educationFormSet,
                    "education_expert_formset": education_expert_anketa_formset,
                }
                return render(request, profile_edit_template, context=context)


        else:

            # Клиент может сохранить свои данные сразу в профиль
            user_form = CustomUserChangeForm(request.POST, instance=request.user)
            profile_form = ProfileChangeForm(request.POST, request.FILES, instance=request.user.profile)

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, _('Your profile is updated successfully'))
                redirect('profile')
            else:
                context = {
                    'user_form': user_form,
                    'profile_form': profile_form,
                }
                return render(request, profile_edit_template, context=context)

        return redirect('profile')
