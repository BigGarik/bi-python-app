from django.utils.text import slugify
import itertools


def generate_unique_slug(instance, title_field_name, slug_field_name):
    """
    Генерирует уникальный слаг для экземпляра модели.

    :param instance: Экземпляр модели, для которого нужно сгенерировать слаг.
    :param title_field_name: Имя поля модели, из которого берется значение для генерации слага.
    :param slug_field_name: Имя поля модели, в которое будет записан сгенерированный слаг.
    """
    # slug_field_name = 'slug'
    model = instance.__class__
    max_length = model._meta.get_field(slug_field_name).max_length
    slug = orig_slug = slugify(getattr(instance, title_field_name))[:max_length]
    for x in itertools.count(1):
        if not model.objects.filter(**{slug_field_name: slug}).exists():
            break
        slug = f"{orig_slug[:max_length - len(str(x)) - 1]}-{x}"
    setattr(instance, slug_field_name, slug)
