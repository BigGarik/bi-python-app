from django.forms import modelformset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic import ListView, DetailView

from web.forms import ArticleForm, ImageForm
from web.models import Article


class ArticleListView(ListView):
    model = Article
    template_name = 'web/article_list.html'


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'web/article_detail.html'


def index(request):
    # return HttpResponse("Hello, world. You're at the polls index.")
    context = {
        "data": "data"
    }
    # return render(request, "web/index.html", context)
    return render(request, "web/index.html", context)


def get_articles(request):
    articles = Article.objects.all()

    data = {
        'title': 'Статьи',
        'articles': articles,
    }

    return render(request, 'web/articles.html', context=data)


def show_article(request, post_slug):
    article = get_object_or_404(Article, slug=post_slug)

    data = {
        'title': article.title,
        'article': article,
        'cat_selected': 1,
    }

    return render(request, 'web/articles.html', context=data)


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")
