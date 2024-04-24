from django import template

register = template.Library()


@register.filter
def filename(value):
    """Возвращает имя файла без пути."""
    return value.split('/')[-1]
