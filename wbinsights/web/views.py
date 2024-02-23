from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseNotFound
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView

from web.models import Article, CustomUser


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email")

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email")

class ArticleListView(ListView):
    model = Article
    template_name = 'article_list.html'


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'article_detail.html'


def index(request):
    # return HttpResponse("Hello, world. You're at the polls index.")
    context = {
        "data": "data"
    }
    # return render(request, "index.html", context)
    return render(request, "index.html", context)


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


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")
