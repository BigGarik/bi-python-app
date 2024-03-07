from django.urls import path

from .views.experts import ExpertListView, ExpertDetailView, SearchByNameExpertListView 
from .views.index import handleIndex
from .views.login import SignUpView
from .views.articles import ArticleDetailView, ArticleListView, ArticleAddView, CategoryArticleListView, create_article  # , add_article
from .views.question_answer import QuestionAnswerListView, QuestionAnswerDetailView, CategoryQuestionAnswerListView
from .views.researches import ResearchesListView, ResearchesDetailView
from django.contrib.auth import views as auth_views
from .views.expert_profile_edit import ProfileEditView



urlpatterns = [
    #path("", handleIndex, name="index"),
    path("", ResearchesListView.as_view(), name="index"),
    # path('profile/<int:pk>/', CustomUserDetailView.as_view(), name='user_profile'),
    # path('profile/<int:pk>/edit/', ProfileUpdateView.as_view(), name='edit_profile'),
   
    path("articles/", ArticleListView.as_view(), name='article_list'),
    path("articles/category/<slug:category_slug>", CategoryArticleListView.as_view(), name='article_category_list'),
    path('articles/<slug:slug>', ArticleDetailView.as_view(), name='article_detail'),
    path("articles/add/", create_article, name='article_add'),
    # path("articles/add/", add_article, name='article_add'),
   
    path("researches/", ResearchesListView.as_view(), name='research_list'),
    path("researches/<slug:slug>", ResearchesDetailView.as_view(), name='research_detail'),
   
    path("question_answer/", QuestionAnswerListView.as_view(), name='question_answer_list'),
    path("question_answer/category/<slug:category_slug>", CategoryQuestionAnswerListView.as_view(), name='question_answer_category_list'),
    path("question_answer/<slug:slug>", QuestionAnswerDetailView.as_view(), name='question_answer_detail'),
   
    path("experts/", ExpertListView.as_view(), name='experts_list'),
    path("experts/category/<slug:category_slug>", ExpertListView.as_view(), name='experts_category_list'),
    path("experts/search/<str:search_str>", SearchByNameExpertListView.as_view(), name='experts_search_list'),
    path("experts/<int:pk>", ExpertDetailView.as_view(), name='expert_profile'),
    path("experts/profile_edit/", ProfileEditView.as_view(), name='expert_profile_edit'),
   
    path("signup/", SignUpView.as_view(), name="signup"),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),

]
