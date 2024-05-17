import itertools
import logging
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core import serializers
from django.core.serializers import json
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from pytils.translit import slugify
from django.db.models import Q
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from web.models import CustomUser, Profile
from .forms import UserProjectForm, UserProjectFileForm
from .models import UserProject, UserProjectFile
from .serializers import UserProjectSerializer, CustomUserSerializer



logger = logging.getLogger(__name__)


class UserProjectDetailView(DetailView):
    model = UserProject
    template_name = 'user_project_detail.html'


class UserProjectCreateView(LoginRequiredMixin, CreateView):
    model = UserProject
    form_class = UserProjectForm
    file_form_class = UserProjectFileForm
    template_name = 'user_project_add.html'

    def form_valid(self, form):
        # Сохранение проекта без коммита
        self.object = form.save(commit=False)
        self.object.author = self.request.user  # Присваиваем текущего пользователя как автора проекта

        # Генерация уникального слага для проекта
        max_length = UserProject._meta.get_field('slug').max_length
        slug = orig_slug = slugify(self.object.name)[:max_length]
        for x in itertools.count(1):
            if not UserProject.objects.filter(slug=slug).exists():
                break
            # Обрезаем оригинальный слаг динамически. Минус 1 для дефиса.
            slug = f"{orig_slug[:max_length - len(str(x)) - 1]}-{x}"
        self.object.slug = slug

        # Сохранение проекта и связанных файлов в одной транзакции
        with transaction.atomic():
            self.object.save()
            form.save_m2m()  # Сохраняем данные many-to-many, включая участников проекта

            # Обработка файлов
            files = self.request.FILES.getlist('files')

            files = self.request.FILES.getlist('files')
            UserProjectFile.objects.bulk_create([
                UserProjectFile(project=self.object, file=file) for file in files
            ])


            # files = self.request.FILES.getlist('files')
            # for file_data in files:
            #     UserProjectFile.objects.create(project=self.object, file=file_data)


            # Обработка участников проекта
            members_ids = self.request.POST.getlist('members')
            if members_ids:
                self.object.members.set(CustomUser.objects.filter(id__in=members_ids))

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'slug': self.object.slug})

    # Метод `get_context_data` добавлен, чтобы включить файловую форму в контекст
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'file_form' not in context:
            context['file_form'] = self.file_form_class()
            # Добавляем список экспертов для элемента выбора участников на форме
        #context['experts'] = CustomUser.objects.filter(profile__type=Profile.TypeUser.EXPERT)
        return context


class UserProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserProject
    form_class = UserProjectForm
    template_name = 'user_project_edit.html'
    context_object_name = 'userproject'

    def test_func(self):
        project = self.get_object()
        return self.request.user == project.author

    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['file_form'] = UserProjectFileForm()
        context['files'] = self.object.files.all()

        context['members_json'] = CustomUserSerializer(self.get_object().members.all(), many=True).data
        context['members'] = self.get_object().members.all()
        context['experts'] = CustomUser.objects.filter(profile__type=Profile.TypeUser.EXPERT)
        return context

    # def post(self, request, *args, **kwargs):
    #     # Получаем список загруженных файлов из объекта FormData
    #     uploaded_files = request.FILES.getlist('files')
    #
    #     # Обрабатываем каждый файл
    #     for uploaded_file in uploaded_files:
    #         # Обрабатываем каждый загруженный файл, например, сохраняем его на сервере
    #         print(uploaded_file)
    #
    #     return JsonResponse({'message': 'Files uploaded successfully!'})

    def form_valid(self, form):
        with transaction.atomic():
            self.object = form.save(commit=False)
            # Генерация уникального слага для проекта
            max_length = UserProject._meta.get_field('slug').max_length
            slug = orig_slug = slugify(self.object.name)[:max_length]
            for x in itertools.count(1):
                if not UserProject.objects.filter(slug=slug).exists():
                    break
                slug = f"{orig_slug[:max_length - len(str(x)) - 1]}-{x}"
            self.object.slug = slug
            self.object.save()
            form.save_m2m()

            # Обработка файлов
            # Add
            files = self.request.FILES.getlist('files')
            for file_data in files:
                UserProjectFile.objects.create(project=self.object, file=file_data)
            # Delite
            delete_files_ids = self.request.POST.getlist('delete_files_ids')
            logger.info(f'delete_files_ids = {delete_files_ids}')
            var_1231 = [5,3]
            logger.info(f'var_1231 = {var_1231}')
            # if delete_files_ids:
            #     logger.info(f'delete_files_ids = {delete_files_ids}')
            #     if isinstance(delete_files_ids, str):
            #         delete_files_ids = delete_files_ids.split(',')
            #         delete_files_ids = [int(number) for number in delete_files_ids]
            #     logger.info(f'delete_files_ids = {delete_files_ids}')
            #     files_to_delete = UserProjectFile.objects.filter(pk__in=delete_files_ids, project__author=self.request.user)
            #     files_to_delete.delete()

            # Обработка участников проекта
            members_ids = self.request.POST.getlist('members')  # Используем getlist для безопасного получения списка
            if members_ids:
                self.object.members.set(CustomUser.objects.filter(id__in=members_ids))
            else:
                self.object.members.clear()

        return HttpResponseRedirect(self.get_success_url())


class UserProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = UserProject
    template_name = 'user_project_confirm_delete.html'
    success_url = reverse_lazy('profile')


@login_required
@require_POST
def project_file_delete(request, pk):
    file = get_object_or_404(UserProjectFile, pk=pk, project__member=request.user)
    project = file.project
    file.delete()
    return HttpResponseRedirect(reverse('project_edit', kwargs={'slug': project.slug}))


class SearchExpertsAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Требуется аутентификация

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query', '')
        if query:
            experts = CustomUser.objects.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query),
                profile__type=Profile.TypeUser.EXPERT
            )
        else:
            # Если параметры не указаны, возвращаем полный список экспертов
            experts = CustomUser.objects.filter(profile__type=Profile.TypeUser.EXPERT)

        # Использование сериализатора для сериализации данных
        serializer = CustomUserSerializer(experts, many=True)
        return JsonResponse({'data':serializer.data})


# Класс для настройки пагинации
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100  # Установите размер страницы для пагинации по умолчанию


class GetProjectsAPIView(ListAPIView):
    serializer_class = UserProjectSerializer
    permission_classes = [IsAuthenticated]  # Требуется аутентификация
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Определите белый список разрешенных полей
        allowed_fields = {'author', 'members', 'category', 'key_results', 'customer', 'year', 'goals'}
        query_params = self.request.query_params

        # Создаем объект Q для динамического построения запроса
        query = Q()
        for param, value in query_params.items():
            # Для поля 'name' используем фильтр 'icontains' для поиска по подстроке
            if param == 'name':
                query &= Q(**{f'{param}__icontains': value})
            # Добавляем условия фильтрации для остальных параметров запроса
            elif param in allowed_fields:
                query &= Q(**{param: value})

        # Фильтруем проекты с использованием созданного запроса
        return UserProject.objects.filter(query)

    def get_serializer(self, *args, **kwargs):
        # Получаем список полей, если он передан в параметрах запроса
        fields = self.request.query_params.get('fields')
        fields = fields.split(',') if fields else None
        # Передаем список полей в сериализатор
        kwargs['context'] = self.get_serializer_context()
        if fields is not None:
            kwargs['fields'] = fields
        return self.serializer_class(*args, **kwargs)
