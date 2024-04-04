from django.shortcuts import render
from django.views.generic import DetailView
from expertprojects.models import UserProject


class UserProjectDetailView(DetailView):
    model = UserProject
    template_name = 'templates/user_project_detail.html'
