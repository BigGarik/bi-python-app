from django import forms
from web.models import Article


class ArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ['title', 'description', 'content', 'main_img', 'cat', 'is_published']
