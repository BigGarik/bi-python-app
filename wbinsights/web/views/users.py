from django.views.generic import ListView, DetailView

from web.models import CustomUser


class CustomUserListView(ListView):
    model = CustomUser
    template_name = 'posts/users/users_list.html'


class CustomUserDetailView(DetailView):
    model = CustomUser
    template_name = 'posts/users/user_profile.html'
