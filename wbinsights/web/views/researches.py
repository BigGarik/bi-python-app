from django.views import View
from django.views.generic import ListView, DetailView

from views.experts import ExpertListView
from web.models import Research
import re


class DeviceDetectionView(View):
    def get(self, request, *args, **kwargs):
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        is_mobile = bool(re.search(r'iphone|android|blackberry|mobile|windows\sphone', user_agent, re.I))
        if is_mobile:
            return ExpertListView.as_view()(request, *args, **kwargs)
        else:
            return ResearchesListView.as_view()(request, *args, **kwargs, extra_context={'is_mobile': False})



class ResearchesListView(ListView):
    model = Research
    template_name = 'posts/research/research_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_mobile'] = self.request.GET.get('is_mobile', 'false') == 'true'
        return context

class ResearchesDetailView(DetailView):
    model = Research
    template_name = 'posts/research/research_detail.html'