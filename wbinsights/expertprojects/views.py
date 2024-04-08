import itertools

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import DetailView, CreateView
from pytils.translit import slugify
from expertprojects.forms import UserProjectForm
from expertprojects.models import UserProject


class UserProjectDetailView(DetailView):
    model = UserProject
    template_name = 'user_project_detail.html'


class UserProjectCreateView(LoginRequiredMixin, CreateView):  # Нужен ли LoginRequiredMixin ???
    model = UserProject
    form_class = UserProjectForm
    template_name = 'user_project_add.html'

    def form_valid(self, form):
        userproject = form.save(commit=False)  # Do not save the article yet
        max_length = UserProject._meta.get_field('slug').max_length
        userproject.slug = orig_slug = slugify(userproject.name)[:max_length]

        for x in itertools.count(1):
            if not UserProject.objects.filter(slug=userproject.slug).exists():
                break
            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            userproject.slug = "%s-%d" % (orig_slug[:max_length - len(str(x)) - 1], x)
        userproject.member = self.request.user  # Присваиваем текущего пользователя как члена проекта
        userproject.save()
        return super().form_valid(form)
