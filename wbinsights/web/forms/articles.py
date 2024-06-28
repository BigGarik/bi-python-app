from django import forms
from django.forms import ClearableFileInput

from web.models import Article


class ArticleClearableFileInput(ClearableFileInput):
    template_name = 'widgets/article_clearable_file_input.html'

class ArticleForm(forms.ModelForm):

    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label="Заголовок")
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}),label="Краткое описание")
    content = forms.CharField(widget=forms.HiddenInput())
    main_img = forms.FileField(label="Главная картинка", widget=ArticleClearableFileInput(
        attrs={'class': 'form-control'},
    ))



    class Meta:
        model = Article
        fields = ['title', 'description', 'content', 'main_img', 'cat', 'is_published', 'styles']
        widgets = {
            'cat': forms.Select(attrs={'class': 'form-control'}),
            'is_published': forms.Select(attrs={'class': 'form-control'})
        }
