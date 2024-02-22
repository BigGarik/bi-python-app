from django.urls import path

from . import views
from .views import ArticleListView, ArticleDetailView

urlpatterns = [
    path("", views.index, name="index"),
    path("articles/", ArticleListView.as_view(), name='article_list'),
    path('articles/<slug:slug>', ArticleDetailView.as_view(), name='article_detail'),
]
