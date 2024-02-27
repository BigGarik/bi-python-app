from django import forms
from django.contrib.auth.forms import PasswordChangeForm

from .models import Article, Image, Research, QuestionAnswer, CustomUser
from .models.users import Profile


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name']


class UserChangeForm(PasswordChangeForm):
    class Meta:
        model = CustomUser
        fields = ['old_password', 'new_password1', 'new_password2']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']


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
