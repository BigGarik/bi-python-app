from django import template

from web.models import Expert

register = template.Library()


@register.simple_tag
def get_top_experts():
    return Expert.objects.all()[:10]


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


