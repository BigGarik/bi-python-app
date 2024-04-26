from django import forms
from web.models import Article, Category


class ArticleForm(forms.ModelForm):

    class Meta:
        model = Article
        fields = ['title', 'description', 'content', 'main_img', 'cat', 'is_published']

    def __init__(self, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        self.fields['cat'].queryset = Category.objects.all()
        self.fields['cat'].label_from_instance = lambda obj: "%s" % obj.name
