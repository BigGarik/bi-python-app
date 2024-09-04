from django.urls import path
from . import views

app_name = 'qa'

urlpatterns = [
    path('', views.question_list, name='question_list'),
    path('question/<int:pk>/', views.question_detail, name='question_detail'),
    path('question/new/', views.create_question, name='create_question'),
    path('answer/<int:answer_id>/best/', views.choose_best_answer, name='choose_best_answer'),

]
