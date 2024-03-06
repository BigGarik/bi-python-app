from typing import Any
from django.urls import reverse
from django.views.generic import ListView, DetailView, UpdateView

from django.shortcuts import render, get_object_or_404

#from web.forms.users import ProfileForm, UserPasswordChangeForm, CustomUserForm
from web.models import CustomUser, Expert
from web.forms.articles import ArticleForm
from web.models import Article, Category

from django.db.models import Q


class ExpertListView(ListView):
    model = Expert
    template_name = 'posts/expert/expert_list.html'
    context_object_name = "experts"
    
    # def get_queryset(self):
        
    #     articles = Article.objects.all()[:2]
    #     return articles
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        
        return context
    
#Класс-представление для фильтрации статей по категории
class SearchByNameExpertListView(ExpertListView):
    #Переопределяем метод получения списка сущностей

    def get_queryset(self):    
        return Expert.objects.filter( Q(first_name__contains=self.kwargs['search_str']) | Q(last_name__contains=self.kwargs['search_str']) )
    
    
#Класс-представление для фильтрации статей по категории
# class CategoryExpertListView(ArticleListView):
#     #Переопределяем метод получения списка сущностей
#     def get_queryset(self):
#         #Получаем объект, по которому будем делать фильтрацию
#         self.cat = get_object_or_404(Expert, slug=self.kwargs['category_slug'])
#         return Article.objects.filter(cat=self.cat)
    
#      #Добавляем параметры в контекст
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['selected_category'] = self.cat       
#         return context
    
class ExpertDetailView(DetailView):
    model = Expert
    template_name = 'posts/expert/expert_profile.html'
    context_object_name = "expert"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['experts_articles'] = Article.objects.all()[:2]
        context['experts_articles_count'] = Article.objects.count()
        context['experts_researches'] = Article.objects.all()[:2]
        context['experts_researches_count'] = Article.objects.count()
        return context



