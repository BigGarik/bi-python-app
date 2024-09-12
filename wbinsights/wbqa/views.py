from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, CreateView, DetailView

from web.views.contents import CommonContentFilterListView
from wbqa.forms import QuestionForm, AnswerForm
from wbqa.models import Question, Answer


class CreateQuestionView(LoginRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = 'create_question.html'
    success_url = reverse_lazy('wbqa:question_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class QuestionDetailView(LoginRequiredMixin, DetailView):
    model = Question
    template_name = 'question_detail.html'
    context_object_name = 'question'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.object
        user = self.request.user

        # Получаем лучший ответ и остальные ответы
        context['best_answer'] = question.answers.filter(is_best=True).first()
        context['other_answers'] = question.answers.filter(is_best=False).order_by('created_at')

        # Получаем ответы
        user_has_answered = Answer.objects.filter(question=question, author=user).exists()
        context['user_has_answered'] = user_has_answered

        # Условия для отображения формы для ответа:
        # 1. Пользователь не оставил ответ.
        # 2. Вопрос адресован ему или targeted_user пуст.
        # 3. Пользователь не является автором вопроса.
        if (not user_has_answered
                and (question.targeted_user is None or question.targeted_user == user)
                and question.author != user):
            context['form'] = AnswerForm()
        else:
            context['form'] = None

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        question = self.object
        user = request.user

        user_has_answered = Answer.objects.filter(question=question, author=user).exists()

        # Условия для добавления ответа:
        # 1. Пользователь не оставил ответ.
        # 2. Вопрос адресован пользователю или targeted_user пуст.
        # 3. Пользователь не является автором вопроса.
        if ((not user_has_answered
                and (self.object.targeted_user is None or self.object.targeted_user == request.user))
                and self.object.author != request.user):
            form = AnswerForm(request.POST)
            if form.is_valid():
                answer = form.save(commit=False)
                answer.question = self.object
                answer.author = request.user
                try:
                    answer.save()
                    return redirect('wbqa:question_detail', pk=self.object.pk)
                except IntegrityError:
                    self.render_to_response(self.get_context_data(error_message="You have already answered this question."))
            return self.render_to_response(self.get_context_data())


class QuestionListView(CommonContentFilterListView):
    model = Question
    template_name = 'question_list.html'
    context_object_name = 'questions'
    paginate_by = 10
    ordering_param_new = '-created_at'
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
