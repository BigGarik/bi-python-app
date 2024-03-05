from typing import Any
from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView

#from web.forms.users import ProfileForm, UserPasswordChangeForm, CustomUserForm
from web.models import CustomUser
from web.forms.articles import ArticleForm
from web.models import Article


class ExpertListView(ListView):
    model = CustomUser
    template_name = 'posts/expert/expert_list.html'
    
    # def get_queryset(self):
        
    #     articles = Article.objects.all()[:2]
    #     return articles
    
    # def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
    #     return super().get_context_data(**kwargs)
    
    #     return context
    


class ExpertDetailView(DetailView):
    model = CustomUser
    template_name = 'posts/expert/expert_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['experts_articles'] = Article.objects.all()[:2]
        context['experts_articles_count'] = Article.objects.count()
        context['experts_researches'] = Article.objects.all()[:2]
        context['experts_researches_count'] = Article.objects.count()
        return context



