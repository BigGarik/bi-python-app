from django.views.generic import ListView, DetailView
from web.models.users import NonVerifiedExpert
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class UnverifiedExpertListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'manage/experts/verification/unverified_experts.html'
    model = NonVerifiedExpert
    context_object_name = 'unverified_experts'

    def test_func(self):
        return self.request.user.is_active and self.request.user.is_superuser


class UnverifiedExpertDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = 'manage/experts/verification/unverified_experts_profile.html'
    model = NonVerifiedExpert
    context_object_name = 'unverified_expert'

    def test_func(self):
        return self.request.user.is_active and self.request.user.is_superuser
