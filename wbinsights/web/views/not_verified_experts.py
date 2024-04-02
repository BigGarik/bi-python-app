from django.shortcuts import render, redirect
from django.views import View

from web.forms.users import VerifyExpertForm
from web.models.users import ExpertProfile
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class UnverifiedExpertListView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'admin/experts/verification/unverified_experts.html'

    def get(self, request, *args, **kwargs):
        unverified_experts_ids = ExpertProfile.objects.select_related('user').filter(
            is_verified=ExpertProfile.ExpertVerifiedStatus.NOT_VERIFIED
        ).values_list('user_id', flat=True)

        unverified_experts = CustomUser.objects.in_bulk(list(unverified_experts_ids))
        return render(request, self.template_name, {'unverified_experts': unverified_experts})

    def post(self, request, *args, **kwargs):
        forms = [VerifyExpertForm(request.POST, instance=expert, prefix=str(expert.pk))
                 for expert in
                 ExpertProfile.objects.filter(is_verified=ExpertProfile.ExpertVerifiedStatus.NOT_VERIFIED)]

        # Сохранять изменения только для тех форм, которые были отмечены и прошли валидацию
        for form in forms:
            if form.is_valid() and 'Верифицирован' in form.cleaned_data:
                form.save()

        # Перенаправляем пользователя обратно на страницу с представлением
        return redirect('admin_unverified_experts_list')

    def test_func(self):
        return self.request.user.is_active and self.request.user.is_staff
