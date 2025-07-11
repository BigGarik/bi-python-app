import math
from datetime import datetime

from django import template
from django.db.models import F
from django.template.defaultfilters import escape
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.utils.translation import gettext as _

from web.models import Expert, Category
from web.models.models import KeyIndicator
from web.services.cbr_key_indicators import get_combined_financial_rates
from web.services.rbc_news_parser import fetch_rss_feed, parse_rss_feed
from web.utils import check_is_mobile

register = template.Library()


# def is_mobile(context):
#     request = context['request']
#     user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
#
#     mobile_agents = ['iphone', 'android', 'blackberry', 'windows phone', 'opera mini', 'mobile']
#     if any(mobile_agent in user_agent for mobile_agent in mobile_agents):
#         return True
#     return False


@register.simple_tag(takes_context=True)
def device_is_mobile(context) -> bool:
    return check_is_mobile(context['request'])


@register.simple_tag
def social_share_buttons(url, title, question_pk):
    html = f'''
    
    <div class="list-comments dropdown">
        <i class="bi bi-box-arrow-up-right share-icon"
           id="socialShareDropdown-{question_pk}" data-bs-toggle="dropdown"
           aria-expanded="false"></i>
        <ul class="dropdown-menu social-share-menu"
            aria-labelledby="socialShareDropdown-{question_pk}">
            <div class="shareon" data-url="{escape(url)}"
                 data-title="{escape(title)}" id="shareon-{question_pk}">
                <a class="facebook"></a>
                <a class="twitter"></a>
                <a class="linkedin"></a>
                <a class="telegram"></a>
                <a class="whatsapp"></a>
                <a class="reddit"></a>
                <a class="vkontakte"></a>
                <a class="odnoklassniki"></a>
                <a class="copy-url"></a>
            </div>
        </ul>
    </div>
    '''
    return mark_safe(html)


@register.simple_tag
def back_button(url_name, text):
    url = reverse(url_name)
    escaped_text = escape(text)
    return mark_safe(
        f'<a href="{url}" class="global-back-btn"><i class="bi bi-chevron-left"></i> &nbsp;{escaped_text}</a>')


@register.filter
def truncatechars(value, arg):
    if len(value) <= arg:
        return value
    return value[:arg] + '...'


@register.simple_tag
def get_rate_chipher(rating):
    ratechipher = ''

    if rating == '' or rating is None or rating < 0:
        rating = 0

    if rating > 5:
        rating = 5

    frac, intnum = math.modf(rating)

    for idx in range(int(intnum)):
        ratechipher += 'f'

    if frac > 0:
        ratechipher += 'h'

    e_starts_cnt = 5 - len(ratechipher)

    for idx in range(e_starts_cnt):
        ratechipher += 'e'

    return ratechipher


@register.simple_tag(takes_context=True)
def get_top_experts(context):
    # return Expert.objects.all()[:10]

    request = context['request']

    experts = Expert.objects.filter(expertprofile__isnull=False)

    if 'category' in request.path:
        paths = request.path.split('/')
        previous = ''
        for path in paths:
            if previous == 'category':
                cat = Category.objects.filter(slug=path)
                if cat.exists():
                    experts = experts.filter(expertprofile__expert_categories=cat[0])
                break
            else:
                previous = path

    return experts.order_by(F('expertprofile__rating').desc(nulls_last=True))[:10]


@register.simple_tag
def get_all_categories():
    return Category.objects.all()


@register.simple_tag
def get_all_news():
    rss_url = "https://rssexport.rbc.ru/rbcnews/news/30/full.rss"
    rss_data = fetch_rss_feed(rss_url)
    news_items = parse_rss_feed(rss_data)
    return news_items


@register.simple_tag
def show_cbr_rates():
    key_indicator = KeyIndicator.objects.first()
    if key_indicator:
        # Если данные найдены, вернуть их
        return key_indicator.indicators

    result = get_combined_financial_rates()

    KeyIndicator.objects.create(indicators=result)

    return result


@register.simple_tag
def format_date(date_string):
    try:
        date_obj = datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %z")

        months = {
            1: 'Января',
            2: 'Февраля',
            3: 'Марта',
            4: 'Апреля',
            5: 'Мая',
            6: 'Июня',
            7: 'Июля',
            8: 'Августа',
            9: 'Сентября',
            10: 'Октября',
            11: 'Ноября',
            12: 'Декабря'
        }

        formatted_date = f"{date_obj.day} {months[date_obj.month]} {date_obj.year}"

        return formatted_date
    except:
        return date_string


@register.simple_tag
def get_category_by_slug(slug):
    cat = Category.objects.filter(slug=slug)
    if len(cat) > 0:
        return cat[0]

    return None


@register.simple_tag
def get_write_phrase(cnt, variants):
    variantsArray = variants.split(' ')

    # return str(cnt) + ' $$ ' + variants

    if cnt == 1:
        return variantsArray[0]

    if cnt > 1 and cnt < 5:
        return variantsArray[1]

    return variantsArray[2]


@register.filter
@register.simple_tag
def split(value, key, element=None):
    if len(value) == 0:
        return None
    res = value[1:].split(key)
    if element == 'first':
        return res[0]
    if element == 'last':
        return res[len(res) - 1]
    return res


@register.filter
def get_post_url_or_none(value):
    if value in ['researches', 'experts', 'articles', 'question_answer']:
        return value
    return None


# custom time repush 2
@register.filter
def custom_time_display(datetime_value):
    time_difference = now() - datetime_value
    days_difference = time_difference.days

    if days_difference > 7:
        return datetime_value.strftime('%d.%m.%Y')

    elif days_difference == 1:
        return _('вчера в ') + datetime_value.strftime('%H:%M')

    elif days_difference > 1:

        if days_difference in (2, 3, 4):
            return f'{days_difference} ' + _('дня назад')
        else:
            return f'{days_difference} ' + _('дней назад')
    else:
        # round to the nearest 30 minutes
        total_minutes = int((time_difference.total_seconds() + 900) // 1800) * 30

        hours = total_minutes // 60

        if hours == 0:
            minutes = total_minutes % 60
            if minutes == 0:
                return _('Только что')
            elif minutes == 1:
                return _('1 минута назад')
            else:
                return f'{minutes} ' + _('минут назад')

        elif hours == 1:
            return _('1 час назад')

        elif hours in (2, 3, 4):
            return f'{hours} ' + _('часа назад')

        else:
            return f'{hours} ' + _('часов назад')


register.filter('custom_time_display', custom_time_display)
