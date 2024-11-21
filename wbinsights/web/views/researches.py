from django.views import View
from django.views.generic import ListView, DetailView

from web.views.experts import ExpertListView
from web.models import Research
from web.utils import  is_mobile
import re


class DeviceDetectionView(View):
    def get(self, request, *args, **kwargs):

        if is_mobile():
            return ExpertListView.as_view()(request, *args, **kwargs)
        else:
            return ResearchesListView.as_view()(request, *args, **kwargs, extra_context={'is_mobile': False})



class ResearchesListView(ListView):
    model = Research
    template_name = 'posts/research/research_list.html'

class ResearchesDetailView(DetailView):
    model = Research
    template_name = 'posts/research/research_detail.html'