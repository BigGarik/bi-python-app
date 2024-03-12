from django.urls import path

from .views.experts import ExpertListView, ExpertDetailView, SearchByNameExpertListView 
from .views.index import handleIndex, handleTest
from .views.login import WBIRegisterUser, WBILoginView
from .views.articles import ArticleDetailView, ArticleListView, ArticleAddView, CategoryArticleListView, create_article  # , add_article
from .views.question_answer import QuestionAnswerListView, QuestionAnswerDetailView, CategoryQuestionAnswerListView
from .views.researches import ResearchesListView, ResearchesDetailView
from django.contrib.auth import views as auth_views
from .views.profile import profile_view,  edit_user_profile



urlpatterns = [
    #path("", handleIndex, name="index"),
    path("", ResearchesListView.as_view(), name="index"),
    path("articles/", ArticleListView.as_view(), name='article_list'),
    path("articles/category/<slug:category_slug>", CategoryArticleListView.as_view(), name='article_category_list'),
    path('articles/<slug:slug>', ArticleDetailView.as_view(), name='article_detail'),
    path("articles/add/", create_article, name='article_add'),
   
    path("researches/", ResearchesListView.as_view(), name='research_list'),
    path("researches/<slug:slug>", ResearchesDetailView.as_view(), name='research_detail'),
   
    path("question_answer/", QuestionAnswerListView.as_view(), name='question_answer_list'),
    path("question_answer/category/<slug:category_slug>", CategoryQuestionAnswerListView.as_view(), name='question_answer_category_list'),
    path("question_answer/<slug:slug>", QuestionAnswerDetailView.as_view(), name='question_answer_detail'),
   
    path("experts/", ExpertListView.as_view(), name='experts_list'),
    path("experts/category/<slug:category_slug>", ExpertListView.as_view(), name='experts_category_list'),
    path("experts/search/<str:search_str>", SearchByNameExpertListView.as_view(), name='experts_search_list'),
    path("experts/<int:pk>", ExpertDetailView.as_view(), name='expert_profile'),

    #users
    path("profile", profile_view, name='profile'),
    path("profile/edit", edit_user_profile, name='profile_edit'),
   
    path("login/", WBILoginView.as_view(), name="login"),
    path("signup/", WBIRegisterUser.as_view(), name="signup"),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),

    path('test/', handleTest, name='test'),

]
