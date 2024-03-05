from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView

#from web.forms.users import ProfileForm, UserPasswordChangeForm, CustomUserForm
from web.models import CustomUser


class ExpertListView(ListView):
    model = CustomUser
    template_name = 'posts/expert/expert_list.html'


class ExpertDetailView(DetailView):
    model = CustomUser
    template_name = 'posts/expert/expert_profile.html'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['profile_form'] = ProfileForm(instance=self.request.user.profile)
    #     context['user_change_form'] = UserPasswordChangeForm(self.request.user)
    #     return context



