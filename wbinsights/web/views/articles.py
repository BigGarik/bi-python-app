from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView

from web.models import Article

def get_articles(request):
    articles = Article.objects.all()

    data = {
        'title': 'Статьи',
        'articles': articles,
    }

    return render(request, 'articles.html', context=data)


def show_article(request, post_slug):
    article = get_object_or_404(Article, slug=post_slug)

    data = {
        'title': article.title,
        'article': article,
        'cat_selected': 1,
    }

    return render(request, 'articles.html', context=data)


class ArticleListView(ListView):
    model = Article
    template_name = 'posts/article/article_list.html'


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'posts/article/article_detail.html'