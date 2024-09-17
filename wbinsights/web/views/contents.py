from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import ListView

from web.models import Category


class CommonContentFilterListView(ListView):
    load_more_template = ''
    category_filter_param = 'cat'
    ordering_param_new = '-time_create'
    ordering_param_popular = '-time_create'

    def get_search_query(self, query):
        return Q(content__icontains=self.query) | Q(title__icontains=self.query)

    def get_queryset(self):

        objects = super().get_queryset()

        self.query = self.request.GET.get('search_q')

        if self.query:
            objects = objects.filter(self.get_search_query(self.query))

        self.cat = ''

        if 'category_slug' in self.kwargs:

            if self.kwargs['category_slug'] == 'new':
                objects = objects.order_by(self.ordering_param_new)
            elif self.kwargs['category_slug'] == 'popular':
                objects = objects.order_by(self.ordering_param_popular)
            else:
                # Получаем объект, по которому будем делать фильтрацию (категория)
                self.cat = get_object_or_404(Category, slug=self.kwargs['category_slug'])
                objects = objects.filter(**{self.category_filter_param: self.cat})

        return objects

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.cat
        context['search_q'] = self.query if self.query is not None else ''
        context['has_more_objects'] = context['page_obj'].has_next()
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string(self.load_more_template, {'object_list': context['object_list']})
            return JsonResponse({
                'html': html,
                'has_more': context['has_more_objects']
            })
        return super().render_to_response(context, **response_kwargs)
