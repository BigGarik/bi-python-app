from django.views.generic import ListView, DetailView
from web.models import Research


class ResearchesListView(ListView):
    model = Research
    template_name = 'posts/research/research_list.html'


class ResearchesDetailView(DetailView):
    model = Research
    template_name = 'posts/research/research_detail.html'
