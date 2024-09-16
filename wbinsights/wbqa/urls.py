from django.urls import path
from . import views
from wbqa.views import AnswerEditView, EditQuestionView, QuestionListView, CreateQuestionView, QuestionDetailView

app_name = 'wbqa'

urlpatterns = [
    path('', QuestionListView.as_view(), name='question_list'),
    path('question/<int:pk>/', QuestionDetailView.as_view(), name='question_detail'),
    path('question/new/', CreateQuestionView.as_view(), name='create_question'),
    path('answer/<int:answer_id>/best/', views.choose_best_answer, name='choose_best_answer'),
    path('question/<int:pk>/edit/', EditQuestionView.as_view(), name='edit_question'),  # Маршрут для редактирования вопроса
    path('answer/<int:pk>/edit/', AnswerEditView.as_view(), name='edit_answer'),  # Маршрут для редактирования ответа

]