import itertools
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from pytils.translit import slugify

from web.forms.articles import ArticleForm
from web.models import Article, Category
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required

# from django.urls import reverse_lazy

import time


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

    # Название переменной для списка статей вместо object_list
    # context_object_name = articles

    # Добавляем параметры в контекст
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['categories'] = Category.objects.all()
        context['selected_category'] = ''
        return context


# Класс-представление для фильтрации статей по категории
class CategoryArticleListView(ArticleListView):
    # Переопределяем метод получения списка сущностей
    def get_queryset(self):

        self.cat = ''
        if self.kwargs['category_slug'] == 'new':
            return Article.objects.all().order_by("time_create")

        if self.kwargs['category_slug'] == 'popular':
            return Article.objects.all().order_by("time_create")

        # Получаем объект, по которому будем делать фильтрацию (категория)
        self.cat = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return Article.objects.filter(cat=self.cat)

    # Добавляем параметры в контекст
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_category'] = self.cat
        return context


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'posts/article/article_detail.html'


@login_required
def create_article(request):
    if request.method == "POST":
        data = request.POST

        article = Article()
        article.title = data['title']
        article.description = data['description']
        article.content = data['content']
        article.main_img = request.FILES.get('main_img')
        article.author = request.user
        max_length = Article._meta.get_field('slug').max_length
        article.slug = slugify(article.title + '-' + str(time.time()))[:max_length]

        # selectedCategorySlug = data['category']
        # if not selectedCategorySlug:
        selected_category = data['category']
        if not selected_category:
            print("Error")

        try:
            # categoryFromDB = Category.objects.get(slug=selectedCategorySlug)
            category_from_db = Category.objects.get(name=selected_category)
            article.cat = category_from_db
            article.save()  # Save the article instance to the database
        except Category.DoesNotExist:
            print("Category not found")

        resp = {
            "toUrl": "articles/"
        }

        return JsonResponse(resp)

    allCategories = Category.objects.all()
    context = {
        "categories": allCategories
    }

    return render(request, 'posts/article/article_add.html', context=context)


@login_required
def edit_article(request, slug):
    article = get_object_or_404(Article, slug=slug, author=request.user)
    form = ArticleForm(instance=article)
    # You may want to add additional logic here as needed
    return render(request, 'posts/article/article_add.html', {'form': form})


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
