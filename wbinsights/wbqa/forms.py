from django import forms

from web.models import Category, CustomUser
from wbqa.models import Question, Answer


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'content', 'targeted_user', 'cat']
        labels = {
            'title': 'Заголовок',
            'content': 'Содержание',
        }

    cat = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Выберите категорию вопроса",
        label="Категория *",
        widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
        required=True
    )

    targeted_user = forms.ModelChoiceField(
        queryset=CustomUser.objects.all(),
        empty_label="Выберите пользователя (необязательно)",
        label="Получатель",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' in field.widget.attrs:
                field.widget.attrs['class'] += ' form-control'
            else:
                field.widget.attrs['class'] = 'form-control'

        # Optionally, you can add placeholders here as well
        self.fields['title'].widget.attrs['placeholder'] = 'Введите заголовок вопроса'
        self.fields['content'].widget.attrs['pl ceholder'] = 'Введите содержание вопроса'

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }