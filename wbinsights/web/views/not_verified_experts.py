import io

from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from django.views.generic import ListView, DetailView

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from wbinsights.settings import SERVER_EMAIL
from web.models.users import ExpertProfile
from web.models.users import ExpertAnketa


#CustomUser = get_user_model()

class UnverifiedExpertListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'manage/experts/verification/unverified_experts.html'
    model = ExpertAnketa
    context_object_name = 'experts_anketas'

    def get_queryset(self):
        return ExpertAnketa.objects.filter(is_verified=ExpertAnketa.AnketaVerifiedStatus.NOT_VERIFIED)

    def test_func(self):
        return self.request.user.is_active and self.request.user.is_superuser


# class UnverifiedExpertDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
#     template_name = 'manage/experts/verification/unverified_experts_profile.html'
#     model = NonVerifiedExpert
#     context_object_name = 'unverified_expert'
#
#     def test_func(self):
#         return self.request.user.is_active and self.request.user.is_superuser
#
#     def post(self, request, *args, **kwargs):
#         action = request.POST.get('action')
#         expert = self.get_object()
#         if action == 'approve':
#             expert.expertprofile.is_verified = ExpertProfile.AnketaVerifiedStatus.VERIFIED
#             # Создаем словарь с данными текущего профиля эксперта
#             expert_data = model_to_dict(expert.expertprofile, exclude=['expert_categories', 'experience_documents', 'educations'])
#             # Удаляем поля
#             expert_data.pop('id', None)
#             expert_data.pop('type_profile', None)
#
#             # Получаем экземпляр CustomUser по ID
#             user_instance = get_object_or_404(CustomUser, id=expert_data.pop('user'))
#
#             # Создаем новый экземпляр ExpertProfile с данными из анкеты
#             verified_expert_profile = ExpertProfile(user=user_instance, **expert_data)
#             verified_expert_profile.type_profile = ExpertProfile.TypeProfile.VERIFIED_PROFILE
#
#             # Копируем связанные категории экспертности
#             if 'expert_categories' in expert_data:
#                 category_ids = expert_data['expert_categories']
#                 verified_expert_profile.expert_categories.set(category_ids)
#
#             # Копируем связанные документы
#             if 'experience_documents' in expert_data:
#                 document_ids = expert_data['experience_documents']
#                 verified_expert_profile.documents.set(document_ids)
#
#             # Копируем связанные образования
#             if 'educations' in expert_data:
#                 education_ids = expert_data['educations']
#                 verified_expert_profile.educations.set(education_ids)
#
#             # verified_expert_profile.expert_categories.set(expert.expertprofile.expert_categories.all())
#             # verified_expert_profile.documents.set(expert.expertprofile.experience_documents.all())
#             # verified_expert_profile.educations.set(expert.expertprofile.educations.all())
#
#             verified_expert_profile.save()
#             expert.expertprofile.save()
#
#             # Перенаправление после подтверждения
#             return redirect('manage_unverified_experts_list')
#         elif action == 'deny':
#             # Перенаправление после отказа
#             return redirect('manage_unverified_experts_list')


# def update_expert_profile(json_data, expert_profile_instance):
#     # Создаем поток данных из JSON-строки
#     stream = io.BytesIO(json_data.encode('utf-8'))
#
#     # Парсим данные с помощью JSONParser
#     data = JSONParser().parse(stream)
#
#     # Создаем экземпляр сериализатора с данными
#     serializer = ExpertProfileSerializer(expert_profile_instance, data=data)
#
#     # Проверяем валидность данных и сохраняем их
#     if serializer.is_valid():
#         serializer.save()
#         return serializer.data
#     else:
#         print(serializer.errors)
#         return None


class UnverifiedExpertDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = 'manage/experts/verification/unverified_experts_profile.html'
    model = ExpertAnketa
    context_object_name = 'unverified_expertanketa'

    def test_func(self):
        return self.request.user.is_active and self.request.user.is_superuser

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        #Сохранение анкеты в профиль
        action = request.POST.get('action')
        expert_anketa: ExpertAnketa = self.get_object()

        if action == 'approve':

            try:
                expert_profile: ExpertProfile = expert_anketa.user.expertprofile
            except Exception as e:
                #if expert_profile doesn't exist
                expert_profile = ExpertProfile()
                expert_profile.user = expert_anketa.user
                expert_profile.save()

            expert_profile.experience = expert_anketa.experience
            expert_profile.age = expert_anketa.age
            expert_profile.expert_categories.set(expert_anketa.expert_categories.all())
            expert_profile.about = expert_anketa.about
            expert_profile.documents.set(expert_anketa.documents.all())
            expert_profile.education.set(expert_anketa.education.all())
            expert_profile.consulting_experience = expert_anketa.consulting_experience
            expert_profile.hour_cost = expert_anketa.hour_cost
            expert_profile.hh_link = expert_anketa.hh_link
            expert_profile.linkedin_link = expert_anketa.linkedin_link
            expert_profile.save()

            expert_anketa.is_verified = ExpertAnketa.AnketaVerifiedStatus.VERIFIED
            expert_anketa.save()

            #moderators = CustomUser.objects.filter(is_staff=True)
            recipient_list = [expert_anketa.user.email]
            html_content = render_to_string('emails/anketa_approved.html',{})
            text_content = strip_tags(html_content)

            # Создаем объект EmailMultiAlternatives
            email = EmailMultiAlternatives(
                'Верификация анкеты',
                text_content,
                SERVER_EMAIL,
                recipient_list
            )
            # Добавляем HTML версию
            email.attach_alternative(html_content, "text/html")
            email.send()

            # Перенаправление после подтверждения
            return redirect('manage_unverified_experts_list')

        elif action == 'deny':
            # Перенаправление после отказа
            return redirect('manage_unverified_experts_list')
