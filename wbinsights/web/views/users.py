from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView

from web.forms.users import ProfileForm, UserChangeForm, CustomUserForm
from web.models import CustomUser


class CustomUserListView(ListView):
    model = CustomUser
    template_name = 'posts/users/users_list.html'


class CustomUserDetailView(DetailView):
    model = CustomUser
    template_name = 'posts/users/user_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_form'] = ProfileForm(instance=self.request.user.profile)
        context['user_change_form'] = UserChangeForm(self.request.user)
        return context


class ProfileUpdateView(UpdateView):
    model = CustomUser
    form_class = CustomUserForm
    second_form_class = ProfileForm
    template_name = 'posts/users/edit_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form2' not in context:
            context['form2'] = self.second_form_class
        return context

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        form2 = self.second_form_class(self.request.POST, self.request.FILES, instance=self.request.user.profile)

        if form2.is_valid():
            form2.save()
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form, form2=form2))

    def get_success_url(self):
        return reverse('user_profile', kwargs={'pk': self.request.user.pk})
