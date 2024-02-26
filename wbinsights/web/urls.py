from django.urls import path

from .views import ResearchesListView, ResearchesDetailView
from .views.index import handleIndex
from .views.login import SignUpView
from .views.articles import ArticleDetailView, ArticleListView

urlpatterns = [
    path("", handleIndex, name="index"),
    path("articles/", ArticleListView.as_view(), name='article_list'),
    path('articles/<slug:slug>', ArticleDetailView.as_view(), name='article_detail'),
    path("researches/", ResearchesListView.as_view(), name='research_list'),
    path("researches/<slug:slug>", ResearchesDetailView.as_view(), name='research_detail'),
    path("signup/", SignUpView.as_view(), name="signup"),
]
