from django.urls import path

from django.contrib import admin
from .views.experts import ExpertListView, ExpertDetailView, SearchByNameExpertListView 
from .views.index import handleIndex #handleTest
from .views.login import register_user, signup_success, activate_account, UserPasswordChangeView, \
    UserForgotPasswordView, UserPasswordResetConfirmView
from .views.articles import ArticleDetailView, ArticleListView, CategoryArticleListView, create_article
from .views.question_answer import QuestionAnswerListView, QuestionAnswerDetailView, CategoryQuestionAnswerListView
from .views.researches import ResearchesListView, ResearchesDetailView
from django.contrib.auth import views as auth_views
from .views.profile import profile_view,  edit_user_profile
from .views.error_404 import wb400handler
from .views.contact import ContactPageView, ContactUsPageView, ContactPoliciesPageView, post_contact_us_form

handler404 = wb400handler

urlpatterns = [
    #path("", handleIndex, name="index"),
    path("", ResearchesListView.as_view(), name="index"),

    path("articles/", ArticleListView.as_view(), name='article_list'),
    path("articles/category/<slug:category_slug>", CategoryArticleListView.as_view(), name='article_category_list'),
    path('articles/<slug:slug>', ArticleDetailView.as_view(), name='article_detail'),
    path("articles/add/", create_article, name='article_add'),
   
    path("researches/", ResearchesListView.as_view(), name='research_list'),
    path("researches/category/<slug:category_slug>", ResearchesListView.as_view(), name='research_category_list'),
    path("researches/<slug:slug>", ResearchesDetailView.as_view(), name='research_detail'),
   
    path("question_answer/", QuestionAnswerListView.as_view(), name='question_answer_list'),
    path("question_answer/category/<slug:category_slug>", CategoryQuestionAnswerListView.as_view(), name='question_answer_category_list'),
    path("question_answer/<slug:slug>", QuestionAnswerDetailView.as_view(), name='question_answer_detail'),
   
    path("experts/", ExpertListView.as_view(), name='experts_list'),
    path("experts/category/<slug:category_slug>", ExpertListView.as_view(), name='experts_category_list'),
    path('experts/search/', SearchByNameExpertListView.as_view(), name='experts_search_list'),
    #path("experts/search/<str:search_str>", SearchByNameExpertListView.as_view(), name='experts_search_list'),
    path("experts/<int:pk>", ExpertDetailView.as_view(), name='expert_profile'),
    
    path("contact/", ContactPageView.as_view(), name='contact'),
    path("contact_us/", ContactUsPageView.as_view(), name='contact_us'),
    path("contact_us/send/", post_contact_us_form, name='contact_us_send'),
    path("data_policies/", ContactPoliciesPageView.as_view(), name='data_policies'),

    #users
    path("profile", profile_view, name='profile'),
    path("profile/edit", edit_user_profile, name='profile_edit'),
   
    path("login/", auth_views.LoginView.as_view(next_page='index'), name="login"),
    path("signup/", register_user, name="signup"),
    path("signup/success", signup_success, name="signup_success"),
    path('activate/<activation_key>/', activate_account, name='activate_account'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),

    path('password-change/', UserPasswordChangeView.as_view(), name='password_change'),
    path('password-reset/', UserForgotPasswordView.as_view(), name='password_reset'),
    path('set-new-password/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('admin/', admin.site.urls),

    #path('test/', handleTest, name='test'),

]
