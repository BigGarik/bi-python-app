from django import forms
from .models import Article, Image, Research, QuestionAnswer, CustomUser


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name']


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content', 'cat', 'is_published']


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
