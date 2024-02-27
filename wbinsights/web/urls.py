from django.urls import path

from .views.users import CustomUserListView, CustomUserDetailView
from .views.index import handleIndex
from .views.login import SignUpView
from .views.articles import ArticleDetailView, ArticleListView, ArticleAddView
from .views.question_answer import QuestionAnswerListView, QuestionAnswerDetailView
from .views.researches import ResearchesListView, ResearchesDetailView


urlpatterns = [
    path("", handleIndex, name="index"),
    path("articles/", ArticleListView.as_view(), name='article_list'),
    path('articles/<slug:slug>', ArticleDetailView.as_view(), name='article_detail'),
    path("articles/add/", ArticleAddView.as_view(), name='article_add'),
    path("researches/", ResearchesListView.as_view(), name='research_list'),
    path("researches/<slug:slug>", ResearchesDetailView.as_view(), name='research_detail'),
    path("question_answer/", QuestionAnswerListView.as_view(), name='question_answer_list'),
    path("question_answer/<slug:slug>", QuestionAnswerDetailView.as_view(), name='question_answer_detail'),
    path("experts/", CustomUserListView.as_view(), name='experts_list'),
    path("experts/<int:pk>", CustomUserDetailView.as_view(), name='expert_profile'),
    path("signup/", SignUpView.as_view(), name="signup"),
]
