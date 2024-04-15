import itertools

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from pytils.translit import slugify
from .forms import UserProjectForm, UserProjectEditForm, UserProjectFileForm
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
        userproject = form.save(commit=False)
        max_length = UserProject._meta.get_field('slug').max_length
        userproject.slug = orig_slug = slugify(userproject.name)[:max_length]

        for x in itertools.count(1):
            if not UserProject.objects.filter(slug=userproject.slug).exists():
                break
            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            userproject.slug = "%s-%d" % (orig_slug[:max_length - len(str(x)) - 1], x)
        userproject.member = self.request.user  # Присваиваем текущего пользователя как member проекта
        userproject.save()

        # Теперь обрабатываем файлы
        files = self.request.FILES.getlist('file_field_name')  # Получаем список файлов
        for file_data in files:  # Если файлы были предоставлены, сохраняем каждый
            UserProjectFile.objects.create(project=userproject, file=file_data)

        return super(UserProjectCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'slug': self.object.slug})

    # Метод `get_context_data` добавлен, чтобы включить файловую форму в контекст
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'file_form' not in context:
            context['file_form'] = self.file_form_class()
        return context


class UserProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProject
    form_class = UserProjectForm
    template_name = 'user_project_edit.html'
    context_object_name = 'userproject'

    def get_context_data(self, **kwargs):
        context = super(UserProjectUpdateView, self).get_context_data(**kwargs)
        if 'file_form' not in context:
            context['file_form'] = UserProjectFileForm()
        context['files'] = self.object.files.all()  # Получаем уже загруженные файлы
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            self.object = form.save()

            # Обработка добавления нового файла
            file_form = UserProjectFileForm(self.request.POST, self.request.FILES)
            if file_form.is_valid():
                new_file = file_form.save(commit=False)
                new_file.project = self.object
                new_file.save()

            # Обработка удаления файла
            for file_id in request.POST.getlist('delete_file'):
                file_to_delete = get_object_or_404(UserProjectFile, id=file_id, project=self.object)
                file_to_delete.delete()

            return HttpResponseRedirect(self.get_success_url())

        # Если форма не валидна, перерендер шаблона
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'slug': self.object.slug})


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
