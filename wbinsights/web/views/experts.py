from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, F
from django.views.generic import DetailView

from expertprojects.models import UserProject
from expertprojects.views import GetProjectsView
from web.models.users import Grade
from wbqa.models import Question
from web.models import Article, Category, Expert
from web.views.contents import CommonContentFilterListView

from web.utils import is_mobile_by_request


from django.db.models import Count, F

class ExpertListView(CommonContentFilterListView):
    model = Expert
    context_object_name = "experts"
    template_name = 'posts/expert/expert_list.html'
    paginate_by = 10
    category_filter_param = 'expertprofile__expert_categories'
    ordering_param_new = '-date_joined'
    ordering_param_popular = '-expertprofile__rating'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            expert_article_cnt=Count('article'),
            expert_rating=F('expertprofile__rating')
        )
        min_rating = self.request.GET.get('min_rating')
        if min_rating:
            queryset = queryset.filter(expertprofile__rating__gte=float(min_rating))
        if not bool(queryset.query.order_by):
            queryset = queryset.order_by('-expert_rating', '-expert_article_cnt')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = ''
        context['min_rating'] = self.request.GET.get('min_rating', '')
        context['grades'] = Grade.objects.all()
        return context

    @property
    def load_more_template(self):
        if is_mobile_by_request(self.request):
            return 'posts/expert/expert_list_mobile.html'
        else:
            return 'posts/expert/expert_list_content.html'

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
        # Получаем базовый queryset с аннотациями и фильтрациями из ExpertListView
        queryset = super().get_queryset()

        # Применяем фильтрацию по имени и фамилии, если передан поисковый запрос
        search_query = self.request.GET.get('q')
        if search_query:
            # Разбиваем строку запроса на слова (имя и фамилия)
            search_terms = search_query.split()

            # Если в запросе два слова, проверяем оба варианта
            if len(search_terms) == 2:
                first_term, second_term = search_terms
                queryset = queryset.filter(
                    # Первый вариант: первое слово — имя, второе — фамилия
                    (Q(first_name__icontains=first_term) & Q(last_name__icontains=second_term)) |
                    # Второй вариант: первое слово — фамилия, второе — имя
                    (Q(first_name__icontains=second_term) & Q(last_name__icontains=first_term))
                )
            # Если одно слово в запросе, ищем по имени или фамилии
            else:
                queryset = queryset.filter(
                    Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query)
                )

        return queryset

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

        # Fetch questions targeted to this expert
        expert_questions = Question.objects.filter(targeted_user=self.object).order_by('-created_at')
        context['expert_questions'] = expert_questions
        context['expert_questions_count'] = expert_questions.count()

        return context