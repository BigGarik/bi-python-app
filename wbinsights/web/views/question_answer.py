from django.views.generic import ListView, DetailView
from web.models import QuestionAnswer


class QuestionAnswerListView(ListView):
    model = QuestionAnswer
    template_name = 'posts/question_answer/question_answer_list.html'


class QuestionAnswerDetailView(DetailView):
    model = QuestionAnswer
    template_name = 'posts/question_answer/question_answer_detail.html'
