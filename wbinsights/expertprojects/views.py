import itertools

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from pytils.translit import slugify

from web.models import CustomUser, Profile
from .forms import UserProjectForm, UserProjectFileForm
from .models import UserProject, UserProjectFile


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
            files = self.request.FILES.getlist('file_field_name')
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
        context['experts'] = CustomUser.objects.filter(profile__type=Profile.TypeUser.EXPERT)
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
        context['experts'] = CustomUser.objects.filter(profile__type=Profile.TypeUser.EXPERT)
        return context

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
            files = self.request.FILES.getlist('file_field_name')
            for file_data in files:
                UserProjectFile.objects.create(project=self.object, file=file_data)

            # Обработка участников проекта
            members_ids = self.request.POST.getlist('members')  # Используем getlist для безопасного получения списка
            if members_ids:
                self.object.members.set(CustomUser.objects.filter(id__in=members_ids))
            else:
                self.object.members.clear()

        return HttpResponseRedirect(self.get_success_url())


class UserProjectDeleteView(DeleteView):
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
