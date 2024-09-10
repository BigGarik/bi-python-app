import itertools

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from hitcount.views import HitCountDetailView
from pytils.translit import slugify

from web.views.contents import CommonContentFilterListView
from web.forms.articles import ArticleForm
from web.models import Article, Category
from django.core.paginator import Paginator


class ArticleListView(CommonContentFilterListView):
    model = Article
    template_name = 'posts/article/article_list.html'
    paginate_by = 2 # Show 10 articles per page
    load_more_template = 'posts/article/article_list_content.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.order_by('-time_update')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context





class ArticleDetailView(HitCountDetailView):
    model = Article
    count_hit = True
    template_name = 'posts/article/article_detail.html'
    form_class = ArticleForm


# LoginRequiredMixin, UserPassesTestMixin - должны быть на первом месте, иначе не срабатывает test_func
class ArticleEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    context_object_name = 'article'
    template_name = 'posts/article/article_add.html'
    success_url = 'article_list'

    def form_valid(self, form):
        form.save()
        return redirect(self.get_success_url())

    def test_func(self):
        article = self.get_object()
        return self.request.user == article.author


def delete_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if request.method == 'POST':
        article.delete()
        return redirect('profile')
    return redirect('profile', slug=slug)


class DeleteArticleView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = 'posts/article/article_confirm_delete.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        # Получаем статью по slug
        slug = self.kwargs.get('slug')
        return get_object_or_404(Article, slug=slug)

    # Проверка, является ли пользователь автором статьи
    def test_func(self):
        article = self.get_object()
        return self.request.user == article.author

    # Обработка случая, когда пользователь не прошёл проверку
    def handle_no_permission(self):
        return HttpResponseForbidden("You are not allowed to delete this article.")


class ArticleAddView(CreateView, LoginRequiredMixin):
    model = Article
    form_class = ArticleForm
    context_object_name = 'article'
    template_name = 'posts/article/article_add.html'
    success_url = reverse_lazy('article_list')

    def get_template_names(self):
        # Custom method to choose template based on device type
        if self.request.META.get('HTTP_USER_AGENT'):
            user_agent = self.request.META['HTTP_USER_AGENT']
            if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
                return ['posts/article/article_add_editor_mobile.html']
        return [self.template_name]

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
