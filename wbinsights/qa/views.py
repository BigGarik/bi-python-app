from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView

from web.views.contents import CommonContentFilterListView
from .forms import QuestionForm, AnswerForm
from .models import Question, Answer


@login_required
def create_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()
            return redirect('qa:question_detail', pk=question.pk)
    else:
        form = QuestionForm()
    return render(request, 'create_question.html', {'form': form})


@login_required
def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)

    # Получаем лучший ответ и остальные ответы
    best_answer = question.answers.filter(is_best=True).first()
    other_answers = question.answers.filter(is_best=False).order_by('created_at')

    # Проверяем, оставил ли пользователь уже ответ на этот вопрос
    user_has_answered = Answer.objects.filter(question=question, author=request.user).exists()

    error_message = None

    if request.method == 'POST' and not user_has_answered:
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.author = request.user
            try:
                answer.save()
                return redirect('qa:question_detail', pk=pk)
            except IntegrityError:
                error_message = "You have already answered this question."
    else:
        form = AnswerForm() if not user_has_answered else None

    context = {
        'question': question,
        'form': form,
        'best_answer': best_answer,
        'other_answers': other_answers,
        'user_has_answered': user_has_answered,
        'error_message': error_message
    }

    return render(request, 'question_detail.html', context)


class QuestionListView(CommonContentFilterListView):
    model = Question
    template_name = 'question_list.html'
    context_object_name = 'questions'
    paginate_by = 10
    ordering_param_new = 'created_at'
    ordering_param_popular = '-created_at'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not bool(queryset.query.order_by):
            queryset = queryset.order_by('-updated_at')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context



@login_required
def choose_best_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    if answer.question.author == request.user:
        answer.question.answers.update(is_best=False)  # сбрасываем предыдущий лучший ответ
        answer.is_best = True
        answer.save()
    return redirect('qa:question_detail', pk=answer.question.pk)


class EditQuestionView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = 'edit_question.html'

    def get_object(self, queryset=None):
        # Используем get_object_or_404 для получения вопроса
        return get_object_or_404(Question, pk=self.kwargs.get('pk'))

    def test_func(self):
        # Проверяем, является ли пользователь автором вопроса
        question = self.get_object()
        return self.request.user == question.author

    def get_success_url(self):
        # Перенаправляем на страницу деталей вопроса после успешного редактирования
        return reverse('qa:question_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['question'] = self.get_object()
        return context


class AnswerEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Answer
    fields = ['content']
    template_name = 'edit_answer.html'

    def get_success_url(self):
        return reverse_lazy('qa:question_detail', kwargs={'pk': self.object.question.pk})

    def test_func(self):
        answer = self.get_object()
        return self.request.user == answer.author
