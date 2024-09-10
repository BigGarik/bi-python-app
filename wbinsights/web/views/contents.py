from django.db.models import Q
from django.shortcuts import get_object_or_404


from django.views.generic import ListView

from web.models import Category


class CommonContentFilterListView(ListView):

    def get_queryset(self):

        objects = super().get_queryset()

        self.query = self.request.GET.get('search_q')

        if self.query:
            objects = objects.filter(Q(content__icontains=self.query) | Q(title__icontains=self.query))

        self.cat = ''

        if 'category_slug' in self.kwargs:

            if self.kwargs['category_slug'] == 'new':
                objects = objects.order_by("time_create")
            elif self.kwargs['category_slug'] == 'popular':
                objects = objects.order_by("time_create")
            else:
                # Получаем объект, по которому будем делать фильтрацию (категория)
                self.cat = get_object_or_404(Category, slug=self.kwargs['category_slug'])
                objects = objects.filter(cat=self.cat)

        return objects

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.cat
        context['search_q'] = self.query
        return context

