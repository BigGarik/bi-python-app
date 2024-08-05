import math
from datetime import datetime

from django import template
from django.db.models import F

from web.services.rbc_news_parser import fetch_rss_feed, parse_rss_feed
from web.models import Expert, Category

from django.utils.timezone import now

from django.utils.translation import gettext as _

import requests
import feedparser

register = template.Library()


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


@register.simple_tag
def get_top_experts():
    # return Expert.objects.all()[:10]
    return Expert.objects.filter(expertprofile__isnull=False).order_by(F('expertprofile__rating').desc(nulls_last=True))[:10]



@register.simple_tag
def get_all_categories():
    return Category.objects.all()

def fetch_rss_feed(url):
    response = requests.get(url)
    return response.content

def parse_rss_feed(rss_data):
    feed = feedparser.parse(rss_data)
    filtered_entries = [
        entry for entry in feed.entries
        if hasattr(entry, 'tags') and any(tag.term in ["Бизнес"] for tag in entry.tags)
    ]
    # Sort by published date and get the 10 newest entries
    filtered_entries.sort(key=lambda x: datetime.strptime(x.published, '%a, %d %b %Y %H:%M:%S %z'), reverse=True)
    return filtered_entries[:10]

@register.simple_tag
def get_all_news():
    rss_url = "https://rssexport.rbc.ru/rbcnews/news/100/full.rss"
    rss_data = fetch_rss_feed(rss_url)
    news_items = parse_rss_feed(rss_data)
    return news_items





@register.simple_tag
def get_category_by_slug(slug):
    cat = Category.objects.filter(slug=slug)
    if len(cat) > 0:
        return cat[0]

    return None


@register.simple_tag
def get_write_phrase(cnt, variants):
    ##print(variants)

    variantsArray = variants.split(' ')
    # print(variantsArray)

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
        #round to the nearest 30 minutes
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



