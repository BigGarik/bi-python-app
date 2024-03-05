from django import template

from web.models import Expert

register = template.Library()

@register.simple_tag
def get_top_experts():
    return Expert.objects.all()[:10]