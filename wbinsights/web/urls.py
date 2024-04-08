from django.contrib.auth.views import LoginView
from django.urls import path

from django.contrib import admin

from .views.experts import ExpertListView, ExpertDetailView, SearchByNameExpertListView
from .views.index import handleIndex  # handleTest
from .views.login import register_user, signup_success, activate_account, UserPasswordChangeView, \
    UserPasswordResetView, UserPasswordResetConfirmView, resend_activation_email
from .views.articles import ArticleDetailView, ArticleListView, CategoryArticleListView, create_article
from .views.not_verified_experts import UnverifiedExpertListView, UnverifiedExpertDetailView
from .views.question_answer import QuestionAnswerListView, QuestionAnswerDetailView, CategoryQuestionAnswerListView
from .views.researches import ResearchesListView, ResearchesDetailView
from django.contrib.auth import views as auth_views
from .views.profile import profile_view, edit_user_profile
from .views.error_404 import wb400handler
from .views.contact import ContactPageView, ContactUsPageView, ContactPoliciesPageView, post_contact_us_form, ContactUsSuccessPageView

handler404 = wb400handler

urlpatterns = [
    # path("", handleIndex, name="index"),
    path("", ResearchesListView.as_view(), name="index"),

    path("articles/", ArticleListView.as_view(), name='article_list'),
    path("articles/category/<slug:category_slug>", CategoryArticleListView.as_view(), name='article_category_list'),
    path('articles/<slug:slug>', ArticleDetailView.as_view(), name='article_detail'),
    path("articles/add/", create_article, name='article_add'),

    path("researches/", ResearchesListView.as_view(), name='research_list'),
    path("researches/category/<slug:category_slug>", ResearchesListView.as_view(), name='research_category_list'),
    path("researches/<slug:slug>", ResearchesDetailView.as_view(), name='research_detail'),

    path("question_answer/", QuestionAnswerListView.as_view(), name='question_answer_list'),
    path("question_answer/category/<slug:category_slug>", CategoryQuestionAnswerListView.as_view(),
         name='question_answer_category_list'),
    path("question_answer/<slug:slug>", QuestionAnswerDetailView.as_view(), name='question_answer_detail'),

    path("experts/", ExpertListView.as_view(), name='experts_list'),
    path("experts/category/<slug:category_slug>", ExpertListView.as_view(), name='experts_category_list'),
    path('experts/search/', SearchByNameExpertListView.as_view(), name='experts_search_list'),
    # path("experts/search/<str:search_str>", SearchByNameExpertListView.as_view(), name='experts_search_list'),
    path("experts/<int:pk>", ExpertDetailView.as_view(), name='expert_profile'),

    path('manage/experts/verification/list/', UnverifiedExpertListView.as_view(), name='manage_unverified_experts_list'),
    path('manage/experts/verification/profile/<int:pk>', UnverifiedExpertDetailView.as_view(), name='manage_unverified_experts_profile'),

    path("contact/", ContactPageView.as_view(), name='contact'),
    path("contact_us/", ContactUsPageView.as_view(), name='contact_us'),
    path("contact_us/send/", post_contact_us_form, name='contact_us_send'),
    path("contact_us/send/success", ContactUsSuccessPageView.as_view(), name='contact_us_send_success'),
    path("data_policies/", ContactPoliciesPageView.as_view(), name='data_policies'),

    # users
    path("profile", profile_view, name='profile'),
    path("profile/edit", edit_user_profile, name='profile_edit'),
    path('profile/anketa', profile_view, name='anketa'),

    path("login/", LoginView.as_view(next_page='index'), name="login"),
    path("signup/", register_user, name="signup"),
    path("signup/success", signup_success, name="signup_success"),
    path('activate/<token>/', activate_account, name='activate_account'),
    path('resend_activation/', resend_activation_email, name='resend_activation'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),

    path('password-change/', UserPasswordChangeView.as_view(), name='password_change'),

    path('password-reset/', UserPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_confirm/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),

    path('admin/', admin.site.urls),


]
