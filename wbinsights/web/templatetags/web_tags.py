from django import template

from web.models import Expert, Category

from django.utils.timesince import timesince
from django.utils.timezone import now

from django.utils.translation import gettext as _

register = template.Library()


@register.simple_tag
def get_top_experts():
    return Expert.objects.all()[:10]


@register.simple_tag
def get_all_categories():
    return Category.objects.all()

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
        return res[len(res)-1]
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

