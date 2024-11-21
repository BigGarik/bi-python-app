from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import EmailMultiAlternatives
from django.forms import modelformset_factory
from django.http import JsonResponse, HttpResponseForbidden
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.html import strip_tags
from django.views.decorators.http import require_POST
from django.views.generic import DeleteView

from wbqa.models import Question
from web.models import RatingCalculate, RatingRole
from web.models.users import Education, ExpertAnketa, ExpertProfile, Grade
from wbappointment.models import Appointment
from wbinsights.settings import SERVER_EMAIL
from web.forms.users import ExpertAnketaChangeForm, CustomUserChangeForm, \
    ProfileChangeForm, EducationForm
from web.models import CustomUser, Profile
from django.utils.translation import gettext_lazy as _

from django.shortcuts import render, redirect, get_object_or_404
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
    is_expert = request.user.profile.type == Profile.TypeUser.EXPERT
    get_params = request.GET.copy()
    if 'category' in get_params:
        del get_params['category']
    context = {
        'get_params': get_params
    }
    profile_template = "profile/expert/profile.html"

    if is_expert:
        try:
            expert_profile = request.user.expertanketa
        except Exception as e:
            expertAnketa = ExpertAnketa()
            expertAnketa.user = request.user
            expertAnketa.save()
            expert_profile = request.user.expertanketa

        # Fetch and paginate expert articles
        expert_articles = Article.objects.filter(author=request.user).order_by('-time_update')
        articles_paginator = Paginator(expert_articles, 10)  # Show 10 articles per page
        articles_page = request.GET.get('articles_page', 1)
        try:
            expert_articles_page = articles_paginator.page(articles_page)
        except PageNotAnInteger:
            expert_articles_page = articles_paginator.page(1)
        except EmptyPage:
            expert_articles_page = articles_paginator.page(articles_paginator.num_pages)

        expert_questions = Question.objects.filter(targeted_user=request.user).order_by('-created_at')
        questions_paginator = Paginator(expert_questions, 10)  # Show 10 questions per page
        questions_page = request.GET.get('questions_page', 1)
        try:
            expert_questions_page = questions_paginator.page(questions_page)
        except PageNotAnInteger:
            expert_questions_page = questions_paginator.page(1)
        except EmptyPage:
            expert_questions_page = questions_paginator.page(questions_paginator.num_pages)

        # Fetch and paginate expert projects
        projects_view = GetProjectsView()
        projects_view.request = request
        queryset = projects_view.get_queryset()
        page_size = projects_view.get_paginate_by(queryset)
        paginator_projects = Paginator(queryset, page_size)
        page_projects = request.GET.get('page', 1)
        try:
            projects = paginator_projects.page(page_projects)
        except PageNotAnInteger:
            projects = paginator_projects.page(1)
        except EmptyPage:
            projects = paginator_projects.page(paginator_projects.num_pages)

        experts_appointment_cnt = Appointment.objects.filter(expert=request.user).count()
        projects_count = UserProject.objects.filter(author=request.user).count()
        ratings = RatingCalculate.objects.select_related('role').filter(user=request.user)
        roles = RatingRole.objects.all()
        rating = ExpertProfile.objects.filter(user=request.user).first()

        context.update({
            "experts_articles": expert_articles_page,
            "experts_articles_count": expert_articles.count(),
            "expert_questions": expert_questions_page,
            "expert_questions_count": expert_questions.count(),
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
            "roles": roles,
            "has_more_articles": expert_articles_page.has_next(),
            "has_more_questions": expert_questions_page.has_next(),
        })
    else:
        profile_template = "profile/client/profile.html"
        clients_appointment_cnt = Appointment.objects.filter(client=request.user).count()
        context.update({
            "users_appointment_cnt": clients_appointment_cnt,
            "experts_articles": [],
            "experts_articles_count": 0,
            "experts_researches_count": 0,
            "user_type": Profile.TypeUser.CLIENT
        })

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.GET.get('tab') == 'articles':
            html = render_to_string('posts/article/article_profile_list_content.html',
                                    {'experts_articles': context['experts_articles']})
            return JsonResponse({
                'html': html,
                'has_more': context['has_more_articles']
            })
        elif request.GET.get('tab') == 'questions':
            html = render_to_string('profile_question_list_content.html',
                                    {'expert_questions': context['expert_questions']})
            return JsonResponse({
                'html': html,
                'has_more': context['has_more_questions']
            })

    return render(request, profile_template, context=context)


@login_required
@require_POST
def update_user_timezone(request):
    new_timezone = request.POST.get('timezone')
    if new_timezone:
        request.user.profile.timezone = new_timezone
        request.user.profile.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


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

    user_agent = request.META.get('HTTP_USER_AGENT', '')
    if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
        if is_expert:
            profile_edit_template = 'profile/expert/edit_expert_profile_mobile.html'
        else:
            profile_edit_template = 'profile/client/edit_client_profile_mobile.html'
    else:
        if is_expert:
            profile_edit_template = 'profile/expert/edit_profile.html'
        else:
            profile_edit_template = 'profile/client/edit_profile.html'

    if request.method == 'GET':
        user_form = CustomUserChangeForm(instance=request.user)
        profile_form = ProfileChangeForm(instance=request.user.profile)

        if is_expert:
            expert_profile_form = ExpertAnketaChangeForm(instance=request.user.expertanketa)
            expert_profile = ExpertProfile.objects.filter(user=request.user).first()
            if expert_profile:
                if expert_profile.points:
                    points = expert_profile.points
                else:
                    points = 0
            else:
                points = 0
            grade = Grade.objects.get(min_points__lte=points, max_points__gte=points)
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
                'grade': grade,
                "expert_profile_form": expert_profile_form,
                "education_expert_formset": education_expert_formset,
            })

        return render(request, profile_edit_template, context=context)

    if request.method == 'POST':
        if is_expert:
            expert_profile = ExpertProfile.objects.filter(user=request.user).first()
            if expert_profile:
                if expert_profile.points:
                    points = expert_profile.points
                else:
                    points = 0
            else:
                points = 0
            grade = Grade.objects.get(min_points__lte=points, max_points__gte=points)
            user_form = CustomUserChangeForm(request.POST, instance=request.user)
            expert_anketa_form = ExpertAnketaChangeForm(request.POST, instance=request.user.expertanketa)
            educationFormSet = modelformset_factory(Education, form=EducationForm, exclude=[], extra=0)
            education_expert_anketa_formset = educationFormSet(request.POST,
                                                               queryset=request.user.expertanketa.education.all())

            if user_form.is_valid() and expert_anketa_form.is_valid() and education_expert_anketa_formset.is_valid():
                user_form.save()
                updated_expert_anketa = expert_anketa_form.save()
                for form in education_expert_anketa_formset.forms:
                    education = form.save()
                    education.expert = request.user
                    education.save()
                    updated_expert_anketa.education.add(education)

                updated_expert_anketa.is_verified = ExpertAnketa.AnketaVerifiedStatus.NOT_VERIFIED
                updated_expert_anketa.save()

                moderators = CustomUser.objects.filter(is_staff=True)
                recipient_list = [moderator.email for moderator in moderators if moderator.email]
                manage_unverified_experts_profile = request.build_absolute_uri(
                    reverse("manage_unverified_experts_profile", kwargs={"pk": updated_expert_anketa.id}))
                manage_unverified_experts_list = request.build_absolute_uri(reverse("manage_unverified_experts_list"))

                html_content = render_to_string('emails/verification_email.html', {
                    'manage_unverified_experts_profile': manage_unverified_experts_profile,
                    'manage_unverified_experts_list': manage_unverified_experts_list
                })
                text_content = strip_tags(html_content)

                email = EmailMultiAlternatives(
                    'Новая анкета эксперта на проверку',
                    text_content,
                    SERVER_EMAIL,
                    recipient_list
                )
                email.attach_alternative(html_content, "text/html")
                email.send()

                messages.success(request, _('Your profile has successfully been sent for verification'))
                return redirect('profile')

            else:
                context = {
                    "user_form": user_form,
                    "profile_form": expert_anketa_form,
                    "expert_profile_form": educationFormSet,
                    "education_expert_formset": education_expert_anketa_formset,
                    'grade': grade,
                }
                return render(request, profile_edit_template, context=context)

        else:
            user_form = CustomUserChangeForm(request.POST, instance=request.user)
            profile_form = ProfileChangeForm(request.POST, request.FILES, instance=request.user.profile)

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, _('Your profile is updated successfully'))
                return redirect('profile')
            else:
                context = {
                    'user_form': user_form,
                    'profile_form': profile_form,
                }
                return render(request, profile_edit_template, context=context)

    return redirect('profile')


class DeleteEducationView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Education
    success_url = reverse_lazy('profile_edit')

    def get_object(self, queryset=None):
        education_id = self.kwargs.get('education_id')
        return get_object_or_404(Education, id=education_id)

    def test_func(self):
        education = self.get_object()
        expert_anketa = ExpertAnketa.objects.get(user=self.request.user)
        return expert_anketa.education.filter(id=education.id).exists()

    def handle_no_permission(self):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': "You are not allowed to delete this education record."
            }, status=403)
        return HttpResponseForbidden("You are not allowed to delete this education record.")

    def delete(self, request, *args, **kwargs):
        education = self.get_object()
        expert_anketa = ExpertAnketa.objects.get(user=self.request.user)
        expert_anketa.education.remove(education)
        education.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': "Education record successfully deleted."
            })

        messages.success(self.request, "Education record successfully deleted.")
        return redirect(self.success_url)

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)
