from django import forms
from web.models import QuestionAnswer


class QuestionAnswerForm(forms.ModelForm):
    class Meta:
        model = QuestionAnswer
        fields = ['title']
