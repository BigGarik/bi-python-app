from django import forms
from web.models import Article


class ArticleForm(forms.ModelForm):

    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    content = forms.CharField(widget=forms.HiddenInput())


    class Meta:
        model = Article
        fields = ['title', 'description', 'content', 'main_img', 'cat', 'is_published']
        widgets = {
            'cat': forms.Select(attrs={'class': 'form-control'}),
            'is_published': forms.Select(attrs={'class': 'form-control'})
        }
