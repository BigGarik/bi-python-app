from django.views.generic import ListView, DetailView
from web.models import QuestionAnswer, Category
from django.shortcuts import get_object_or_404


class QuestionAnswerListView(ListView):
    model = QuestionAnswer
    template_name = 'posts/question_answer/question_answer_list.html'

    def get_context_data(self, **kwargs):       
        context = super().get_context_data(**kwargs)        
        context['categories'] = Category.objects.all()
        return context
    
class CategoryQuestionAnswerListView(QuestionAnswerListView):
    
    def get_queryset(self):
        self.cat = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return QuestionAnswer.objects.filter(cat=self.cat)


class QuestionAnswerDetailView(DetailView):
    model = QuestionAnswer
    template_name = 'posts/question_answer/question_answer_detail.html'
