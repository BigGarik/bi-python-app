#import debug_toolbar
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from wbqa.views import QuestionListView
from .utils import get_timezones
from .views.articles import (ArticleDetailView, ArticleAddView, ArticleEditView, ArticleListView, DeleteArticleView)
from .views.contact import ContactPageView, ContactUsPageView, ContactPoliciesPageView, post_contact_us_form, \
    ContactUsSuccessPageView
from .views.crb_key import CrbRatesView
from .views.error_404 import wb400handler
from .views.experts import ExpertListView, ExpertDetailView, SearchByNameExpertListView
from .views.user import register_user, signup_success, activate_account, UserPasswordChangeView, \
    UserPasswordResetView, UserPasswordResetConfirmView, resend_activation_email, CustomLoginView, UserDeleteView
from .views.news import NewsFeedView
from .views.not_verified_experts import UnverifiedExpertListView, UnverifiedExpertDetailView
from .views.profile import profile_view, edit_user_profile, update_user_timezone, DeleteEducationView
from .views.rating import RatingListView
from .views.researches import ResearchesListView, ResearchesDetailView, DeviceDetectionView
from .views.vote import upvote, downvote, universal_vote

handler404 = wb400handler

urlpatterns = [
    path("", DeviceDetectionView.as_view(), name="index"),

    path('upvote/<int:pk>/', upvote, name='upvote'),
    path('downvote/<int:pk>/', downvote, name='downvote'),
    path('vote/<str:model_name>/<int:pk>/', universal_vote, name='universal_vote'),

    path("articles/", ArticleListView.as_view(), name='article_list'),
    path("articles/category/<slug:category_slug>", ArticleListView.as_view(), name='article_category_list'),
    path('articles/<slug:slug>', ArticleDetailView.as_view(), name='article_detail'),
    path("articles/add/", ArticleAddView.as_view(), name='article_add'),
    path("articles/edit/<slug:slug>/", ArticleEditView.as_view(), name='article_edit'),
    path('articles/delete/<slug:slug>/', DeleteArticleView.as_view(), name='delete_article'),

    path("researches/", ResearchesListView.as_view(), name='research_list'),
    path("researches/category/<slug:category_slug>", ResearchesListView.as_view(), name='research_category_list'),
    path("researches/<slug:slug>", ResearchesDetailView.as_view(), name='research_detail'),

    path("question_answer/", QuestionListView.as_view(), name='question_list'),
    path("question_answer/category/<slug:category_slug>", QuestionListView.as_view(), name='question_category_list'),
    # path("question_answer/<slug:slug>", QuestionAnswerDetailView.as_view(), name='question_answer_detail'),

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
    path('update-timezone/', update_user_timezone, name='update_user_timezone'),
    path('api/timezones/', get_timezones, name='get_timezones'),
    # path('profile/tab/<str:tab>/', profile_view, name='profile_tab'),
    path("profile/edit", edit_user_profile, name='profile_edit'),
    path('education/<int:education_id>/delete/', DeleteEducationView.as_view(), name='delete_education'),
    # path('profile/anketa', profile_view, name='anketa'),
    path('profile/ratings/', RatingListView.as_view(), name='rating-list'),
    #path('profile/anketa/', anketa_view, name='anketa'),
    path('user/delete/', UserDeleteView.as_view(), name='user_delete'),

    path("login/", CustomLoginView.as_view(next_page='index'), name="login"),
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
    # path('calculate_rating/', calculate_rating_for_all_expert, name='calculate_rating_for_all_expert'),
    path('api/news/', NewsFeedView.as_view(), name='news_feed'),
    path('api/crb-rates/', CrbRatesView.as_view(), name='crb_rates'),

    #path('__debug__/', include('debug_toolbar.urls')),   # Закомментировать перед пушем

]
