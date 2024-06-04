import itertools
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from pytils.translit import slugify

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from web.forms.articles import ArticleForm
from web.models import Article, Category
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required

from django.db.models import Q


import time

class ArticleListView(ListView):
    model = Article
    template_name = 'posts/article/article_list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        query = self.request.GET.get('search_q')
        if query:
            return Article.objects.filter(Q(content__icontains=query) | Q(title__icontains=query))
        return Article.objects.all()

    # Добавляем параметры в контекст
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = ''
        context['search_q'] = self.request.GET.get('search_q', '')
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
    form_class = ArticleForm

    def form_valid(self, form):
        return HttpResponseRedirect(self.get_success_url())


class ArticleEditView(UpdateView, LoginRequiredMixin):
    model = Article
    form_class = ArticleForm
    context_object_name = 'article'
    template_name = 'posts/article/article_add.html'
    success_url = 'article_list'

    def form_valid(self, form):
        form.save()
        return redirect(self.get_success_url())


#
#
# @login_required
# def create_article(request):
#
#     if request.method == "POST":
#
#         data = request.POST
#
#         article = Article()
#         article.title = data['title']
#         article.description = data['description']
#         article.content = data['content']
#         article.main_img = request.FILES.get('main_img')
#         article.author = request.user
#         max_length = Article._meta.get_field('slug').max_length
#         article.slug = slugify(article.title + '-' + str(time.time()))[:max_length]
#
#         # selectedCategorySlug = data['category']
#         # if not selectedCategorySlug:
#         selected_category = data['category']
#         if not selected_category:
#             print("Error")
#
#         try:
#             # categoryFromDB = Category.objects.get(slug=selectedCategorySlug)
#             category_from_db = Category.objects.get(name=selected_category)
#             article.cat = category_from_db
#             article.save()  # Save the article instance to the database
#         except Category.DoesNotExist:
#             print("Category not found")
#
#         resp = {
#             "toUrl": "articles/"
#         }
#
#         return JsonResponse(resp)
#
#     allCategories = Category.objects.all()
#     context = {
#         "categories": allCategories
#     }
#
#     return render(request, 'posts/article/article_add.html', context=context)



def delete_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if request.method == 'POST':
        article.delete()
        return redirect('profile')
    return redirect('profile', slug=slug)



class ArticleAddView(CreateView, LoginRequiredMixin):
    model = Article
    form_class = ArticleForm
    context_object_name = 'article'
    template_name = 'posts/article/article_add.html'
    success_url = 'article_list'

    def form_valid(self, form):
        article = form.save(commit=False)  # Do not save the article yet
        article.author = self.request.user
        max_length = Article._meta.get_field('slug').max_length
        article.slug = orig_slug = slugify(article.title)[:max_length]

        for x in itertools.count(1):
            if not Article.objects.filter(slug=article.slug).exists():
                break
            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            article.slug = "%s-%d" % (orig_slug[:max_length - len(str(x)) - 1], x)

        article.save()
        #return redirect(self.get_success_url())
        return super().form_valid(form)
