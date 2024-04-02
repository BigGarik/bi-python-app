from django.shortcuts import render, redirect
from django.views import View

from web.forms.users import VerifyExpertForm
from web.models.users import ExpertProfile
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class UnverifiedExpertListView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'admin/experts/verification/unverified_experts.html'

    def get(self, request, *args, **kwargs):
        experts = ExpertProfile.objects.filter(is_verified=ExpertProfile.ExpertVerifiedStatus.NOT_VERIFIED)
        forms = [VerifyExpertForm(instance=expert, prefix=str(expert.pk)) for expert in experts]
        return render(request, self.template_name, {'forms': forms})

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
