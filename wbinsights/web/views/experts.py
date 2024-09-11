from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, F
from django.views.generic import DetailView

from expertprojects.models import UserProject
from expertprojects.views import GetProjectsView
from web.models import Article, Category, Expert
from web.views.contents import CommonContentFilterListView


class ExpertListView(CommonContentFilterListView):
    model = Expert
    context_object_name = "experts"
    paginate_by = 10
    category_filter_param = 'expertprofile__expert_categories'
    ordering_param_new = '-date_joined'
    ordering_param_popular = '-expertprofile__rating'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Добавление аннотаций для подсчёта количества статей и рейтинга
        queryset = queryset.annotate(
            expert_article_cnt=Count('article'),
            expert_rating=F('expertprofile__rating')
        )

        # Фильтрация по рейтингу
        min_rating = self.request.GET.get('min_rating')
        if min_rating:
            queryset = queryset.filter(expertprofile__rating__gte=float(min_rating))

        # Если нет сортировки, то сортировка по рейтингу и количеству статей
        if not bool(queryset.query.order_by):
            queryset = queryset.order_by('-expert_rating', '-expert_article_cnt')

        return queryset

    def get_template_names(self):
        user_agent = self.request.META.get('HTTP_USER_AGENT','')
        if 'Mobile' in user_agent or 'Andriod' in user_agent or 'Iphone' in user_agent:
            return ['posts/expert/expert_list_mobile.html']
        else:
            return ['posts/expert/expert_list.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = ''
        context['is_mobile'] = True

        return context


class CategoryExpertListView(ExpertListView):
    def get_queryset(self):
        return super().get_queryset()


# def get_expert_not_verified():
#     experts = Expert.objects.filter()
#     experts = ExpertProfile.ExpertVerif.NOT_VERIFIED
#     return experts

# Класс-представление для фильтрации статей по категории
# class SearchByNameExpertListView(ExpertListView):
#     #Переопределяем метод получения списка сущностей

#     def get_queryset(self):    
#         return Expert.objects.filter( Q(first_name__contains=self.kwargs['search_str']) | Q(last_name__contains=self.kwargs['search_str']) )


class SearchByNameExpertListView(ExpertListView):
    # Override the queryset to filter experts by search string

    names1 = "Simple data"

    def get_queryset(self):
        return Expert.objects.filter(
            Q(first_name__contains=self.request.GET.get('q')) | Q(last_name__contains=self.request.GET.get('q')))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_q'] = self.request.GET.get('q')
        context['some_data'] = self.names1
        return context


class ExpertDetailView(DetailView):
    model = Expert
    template_name = 'posts/expert/expert_profile.html'
    context_object_name = "expert"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Remove 'category' from the GET parameters
        get_params = self.request.GET.copy()
        if 'category' in get_params:
            del get_params['category']

        context['get_params'] = get_params

        user_articles_qs = Article.objects.filter(author__id=self.kwargs['pk'])

        context['experts_articles'] = user_articles_qs
        context['experts_articles_count'] = user_articles_qs.count()
        context['experts_researches'] = Article.objects.all()[:2]

        context['experts_researches_count'] = Article.objects.count()
        context['rating'] = 4.5

        projects_count = UserProject.objects.filter(author__id=self.kwargs['pk']).count()

        # Fetch the expert's projects
        projects_view = GetProjectsView()
        projects_view.request = self.request
        queryset = projects_view.get_queryset(user=self.get_object())
        page_size = projects_view.get_paginate_by(queryset)
        paginator = Paginator(queryset, page_size)
        page = self.request.GET.get('page', 1)

        try:
            projects = paginator.page(page)
        except PageNotAnInteger:
            projects = paginator.page(1)
        except EmptyPage:
            projects = paginator.page(paginator.num_pages)

        context['projects'] = projects
        context['projects_count'] = projects_count

        return context
