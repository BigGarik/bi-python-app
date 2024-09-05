from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Question, Answer
from .forms import QuestionForm, AnswerForm


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


@login_required
def question_list(request):
    questions = Question.objects.all()
    return render(request, 'question_list.html', {'questions': questions})


@login_required
def choose_best_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    if answer.question.author == request.user:
        answer.question.answers.update(is_best=False)  # сбрасываем предыдущий лучший ответ
        answer.is_best = True
        answer.save()
    return redirect('qa:question_detail', pk=answer.question.pk)
