from django import forms
from .models import Article, Image, Research, QuestionAnswer


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content']


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['image']


class ResearchForm(forms.ModelForm):
    class Meta:
        model = Research
        fields = ['name']


class QuestionAnswer(forms.ModelForm):
    class Meta:
        model = QuestionAnswer
        fields = ['title']
