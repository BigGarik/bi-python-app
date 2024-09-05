from django import forms

from web.models import Category, CustomUser
from .models import Question, Answer


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'content', 'targeted_user', 'cat']

    # Виджет для выбора категории
    cat = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Выберите категорию вопроса",
        label="Категория *",
        widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
        required=True
    )

    # Переопределим поле 'targeted_user' для отображения first_name и last_name
    targeted_user = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        empty_label="Выберите пользователя",
        label="Получатель",
        widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
        to_field_name='id',
        required=True
    )

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        # Меняем отображение пользователей на "first_name last_name"
        self.fields['targeted_user'].queryset = CustomUser.objects.all().order_by('first_name', 'last_name')
        self.fields['targeted_user'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name}"


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
