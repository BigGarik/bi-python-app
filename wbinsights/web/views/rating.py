from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from web.models import RatingCalculate, RatingRole


class RatingListView(LoginRequiredMixin, ListView):
    model = RatingCalculate
    template_name = 'profile/expert/rating_list.html'
    context_object_name = 'ratings'

    def get_queryset(self):
        return RatingCalculate.objects.select_related('role').filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = RatingRole.objects.all()
        return context
