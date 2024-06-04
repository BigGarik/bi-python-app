import io
import json

from django.db.models.fields.related import ManyToManyField, ForeignKey
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView
from django.core import serializers
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from web.models import Category
from web.models.users import NonVerifiedExpert, ExpertProfile
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model

from web.serializers import create_dynamic_serializer, universal_deserializer, ExpertProfileSerializer

CustomUser = get_user_model()


class UnverifiedExpertListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'manage/experts/verification/unverified_experts.html'
    model = NonVerifiedExpert
    context_object_name = 'unverified_experts'

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
#             expert.expertprofile.is_verified = ExpertProfile.ExpertVerifiedStatus.VERIFIED
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


def update_expert_profile(json_data, expert_profile_instance):
    # Создаем поток данных из JSON-строки
    stream = io.BytesIO(json_data.encode('utf-8'))

    # Парсим данные с помощью JSONParser
    data = JSONParser().parse(stream)

    # Создаем экземпляр сериализатора с данными
    serializer = ExpertProfileSerializer(expert_profile_instance, data=data)

    # Проверяем валидность данных и сохраняем их
    if serializer.is_valid():
        serializer.save()
        return serializer.data
    else:
        print(serializer.errors)
        return None


class UnverifiedExpertDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = 'manage/experts/verification/unverified_experts_profile.html'
    model = NonVerifiedExpert  # объект CustomUser
    context_object_name = 'unverified_expert'

    def test_func(self):
        return self.request.user.is_active and self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expert = self.get_object()
        expert_profile = expert.expertprofile

        # Десериализуем данные из поля anketa
        anketa_data = expert_profile.anketa
        if anketa_data:
            anketa_object = json.loads(anketa_data)
        else:
            anketa_object = None

        # Передаем десериализованные данные в контекст шаблона
        context['anketa'] = anketa_object
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        expert = self.get_object()
        expert_profile = expert.expertprofile

        if action == 'approve':
            # # Сериализация для теста
            # serializer = ExpertProfileSerializer(expert_profile)
            # json_data = JSONRenderer().render(serializer.data)
            # print(json_data.decode('utf-8'))
            # expert_profile.anketa = json_data.decode('utf-8')

            anketa_data = expert_profile.anketa
            if anketa_data:
                # Десериализация данных из JSON
                stream = io.BytesIO(anketa_data.encode('utf-8'))
                data = JSONParser().parse(stream)

                # Создание экземпляра сериализатора с данными
                serializer = ExpertProfileSerializer(data=data).update(expert_profile, data)
            # TODO установить статус Анкеты в верифицирована
            # expert_profile.anketa.is_verified = ExpertProfile.ExpertVerifiedStatus.VERIFIED # пример что бы не забыть
            # expert_profile.is_verified = ExpertProfile.ExpertVerifiedStatus.VERIFIED
            expert_profile.save()

            # Перенаправление после подтверждения
            return redirect('manage_unverified_experts_list')
        elif action == 'deny':
            # Перенаправление после отказа
            return redirect('manage_unverified_experts_list')
