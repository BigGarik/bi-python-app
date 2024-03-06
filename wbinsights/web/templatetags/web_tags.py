from django import template

from web.models import Expert

register = template.Library()

@register.simple_tag
def get_top_experts():
    return Expert.objects.all()[:10]

@register.simple_tag
def get_write_phrase(cnt, variants):

    print(variants)

    variantsArray = variants.split(' ')
    print(variantsArray)

    #return str(cnt) + ' $$ ' + variants

    if cnt == 1:
        return variantsArray[0]
    
    if cnt > 1 and cnt < 5:
        return variantsArray[1]
    
    return variantsArray[2]