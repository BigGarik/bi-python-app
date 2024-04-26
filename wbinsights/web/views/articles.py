from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from wbinsights.utilities import generate_unique_slug
from web.forms.articles import ArticleForm
from web.models import Article, Category
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required


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
        generate_unique_slug(article, 'title', 'slug')
        # max_length = Article._meta.get_field('slug').max_length
        # article.slug = slugify(article.title + '-' + str(time.time()))[:max_length]

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


class ArticleAddView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'posts/article/article_add.html'
    success_url = reverse_lazy('article_list')

    def form_valid(self, form):
        # Устанавливаем автора статьи
        form.instance.author = self.request.user
        # Генерируем уникальный слаг для статьи
        generate_unique_slug(form.instance, 'title', 'slug')
        # Сохраняем статью
        self.object = form.save()
        # Возвращаем JSON-ответ с URL для перенаправления
        return JsonResponse({
            'success': True,
            'redirect_url': self.get_success_url()
        })

    def form_invalid(self, form):
        # Возвращаем JSON-ответ с информацией об ошибках
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def get_success_url(self):
        # Можно указать URL для перенаправления после успешного создания статьи
        return reverse_lazy('articles_list')

    # def form_valid(self, form):
    #     self.object = form.save(commit=False)
    #     generate_unique_slug(self.object, 'title', 'slug')
    #     self.object.save()
    #     return super().form_valid(form)
