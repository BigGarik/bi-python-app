import itertools
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from pytils.translit import slugify

from web.forms.articles import ArticleForm
from web.models import Article

# def get_articles(request):
#     articles = Article.objects.all()
#
#     data = {
#         'title': 'Статьи',
#         'articles': articles,
#     }
#
#     return render(request, 'articles.html', context=data)
#
#
# def show_article(request, post_slug):
#     article = get_object_or_404(Article, slug=post_slug)
#
#     data = {
#         'title': article.title,
#         'article': article,
#         'cat_selected': 1,
#     }
#
#     return render(request, 'articles.html', context=data)


class ArticleListView(ListView):
    model = Article
    template_name = 'posts/article/article_list.html'


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'posts/article/article_detail.html'


class ArticleAddView(CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'posts/article/article_add.html'

    def form_valid(self, form):
        article = form.save(commit=False)  # Do not save the article yet
        max_length = Article._meta.get_field('slug').max_length
        article.slug = orig_slug = slugify(article.title)[:max_length]

        for x in itertools.count(1):
            if not Article.objects.filter(slug=article.slug).exists():
                break
            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            article.slug = "%s-%d" % (orig_slug[:max_length - len(str(x)) - 1], x)

        article.save()
        return super().form_valid(form)
