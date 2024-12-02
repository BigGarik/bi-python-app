import os
import itertools
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.serializers import json
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, ListView
from hitcount.models import HitCount
from hitcount.utils import get_hitcount_model
from hitcount.views import HitCountMixin, HitCountDetailView
from pytils.translit import slugify
from django.db.models import Q, Count
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


logger = logging.getLogger("django-info")


class UserProjectDetailView(HitCountDetailView):
    model = UserProject
    template_name = 'user_project_detail.html'
    count_hit = True  # Включаем подсчет просмотров

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hit_count = get_object_or_404(HitCount, object_pk=self.object.pk, content_type__model='userproject')
        context['hit_count'] = hit_count.hits
        return context

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        hit_count = get_object_or_404(HitCount, object_pk=self.object.pk, content_type__model='userproject')
        hit_count_response = self.hit_count(request, hit_count)
        if hit_count_response.hit_counted:
            hit_count.hits += 1
            hit_count.save()
        return response


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


            files = self.request.FILES.getlist('files')
            UserProjectFile.objects.bulk_create([
                UserProjectFile(project=self.object, file=file) for file in files
            ])

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
            delete_file_ids_str = self.request.POST.getlist('delete_file_ids', [''])[0]
            if delete_file_ids_str:
                delete_file_ids_list_str = delete_file_ids_str.split(',')
                delete_file_ids = [int(file_id) for file_id in delete_file_ids_list_str if file_id.isdigit()]
                files_to_delete = UserProjectFile.objects.filter(id__in=delete_file_ids)
                with transaction.atomic():
                    for file_obj in files_to_delete:
                        file_path = file_obj.file.path
                        if os.path.isfile(file_path):
                            try:
                                os.remove(file_path)
                                file_obj.delete()
                            except OSError as e:
                                logger.error(f"Ошибка при удалении файла {file_path}: {e}")

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
    success_url = reverse_lazy('index')


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
        return JsonResponse({'data': serializer.data})


# Класс для настройки пагинации
class StandardResultsSetPagination(PageNumberPagination):
    def get_page_size(self, request):
        return request.query_params.get('page_size', self.page_size)


class GetProjectsAPIView(ListAPIView, HitCountMixin):
    serializer_class = UserProjectSerializer
    permission_classes = [IsAuthenticated]  # Требуется аутентификация
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Определите белый список разрешенных полей
        allowed_fields = {'author', 'members', 'category', 'key_results', 'company', 'year', 'goals'}
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
        queryset = UserProject.objects.filter(query)

        for project in queryset:
            hit_count = HitCount.objects.get_for_object(project)
            hit_count_response = self.hit_count(request=self.request, hit_count_model=hit_count)
            project.hit_count = hit_count_response.hits
        return queryset

    def get_serializer(self, *args, **kwargs):
        # Получаем список полей, если он передан в параметрах запроса
        fields = self.request.query_params.get('fields')
        fields = fields.split(',') if fields else None
        # Передаем список полей в сериализатор
        kwargs['context'] = self.get_serializer_context()
        if fields is not None:
            kwargs['fields'] = fields
        return self.serializer_class(*args, **kwargs)


@require_POST
@csrf_exempt
def update_hit_count(request, project_id):
    try:
        project = UserProject.objects.get(id=project_id)
        content_type = ContentType.objects.get_for_model(UserProject)
        hit_count, created = HitCount.objects.get_or_create(
            content_type=content_type,
            object_pk=str(project.pk)
        )
        hit_count_response = HitCountMixin.hit_count(request, hit_count)
        hit_counted = hit_count_response.hit_counted
        hit_count.refresh_from_db()
        hit_count_value = hit_count.hits

        return JsonResponse({
            'success': hit_counted,
            'hit_count': hit_count_value
        })
    except Exception as e:
        logger.exception(f"Unexpected error in update_hit_count: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


class GetProjectsView(LoginRequiredMixin, ListView):
    model = UserProject
    context_object_name = 'projects'
    template_name = 'project_list.html'  # Укажите путь к вашему шаблону
    paginate_by = 5  # Установите количество объектов на страницу

    def get_paginate_by(self, queryset):
        # Получаем значение page_size из параметров запроса или используем значение по умолчанию
        page_size = self.request.GET.get('page_size', self.paginate_by)
        try:
            return max(1, int(page_size))  # Преобразуем в int и гарантируем, что значение больше 1
        except (TypeError, ValueError):
            return self.paginate_by

    def get_queryset(self, user=None):
        allowed_fields = {'author', 'members', 'category', 'key_results', 'company', 'year', 'goals'}
        query_params = self.request.GET

        query = Q()
        for param, value in query_params.items():
            # Для поля 'category' проверяем, что значение является числом
            if param == 'category':
                try:
                    value = int(value)  # Преобразуем значение в число
                    query &= Q(**{param: value})
                except ValueError:
                    # Если значение не может быть преобразовано в число, игнорируем этот параметр фильтрации
                    continue
            else:
                # Для поля 'name' используем фильтр 'icontains' для поиска по подстроке
                if param == 'name':
                    query &= Q(**{f'{param}__icontains': value})
                elif param in allowed_fields:
                    query &= Q(**{param: value})

        # Start with all the user's projects
        projects = UserProject.objects.filter(author=user if user else self.request.user)
        return projects.filter(query)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projects = context['projects']

        # Получаем информацию о просмотрах для каждого проекта
        hit_counts = {}
        for project in projects:
            hit_count = HitCount.objects.get_for_object(project)
            hit_counts[project.id] = hit_count.hits

        context['hit_counts'] = hit_counts

        # Debug information
        messages.info(self.request, f"Debug: hit_counts = {hit_counts}")

        return context
