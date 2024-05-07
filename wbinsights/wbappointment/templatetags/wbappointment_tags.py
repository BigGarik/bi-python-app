from django import template

from django.utils.timesince import timesince
from django.utils.timezone import now

from django.utils.translation import gettext as _

from wbappointment.utils import get_expert_schedule_form_set

register = template.Library()

@register.simple_tag
def get_expert_schedule_form_set_tag(request):
    return get_expert_schedule_form_set(request)
