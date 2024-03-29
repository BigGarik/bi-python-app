from django.db import models
from django.urls import reverse


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=Article.Status.PUBLISHED)


# теги
# class Post(models.Model):
#     name = models.CharField(max_length=200)
#     tags = ArrayField(models.CharField(max_length=200), blank=True)

#     def __str__(self):
#         return self.name
# contains¶
# The contains lookup is overridden on ArrayField. The returned objects will be those where the values passed are a subset of the data. It uses the SQL operator @>. For example:

# >>> Post.objects.create(name="First post", tags=["thoughts", "django"])
# >>> Post.objects.create(name="Second post", tags=["thoughts"])
# >>> Post.objects.create(name="Third post", tags=["tutorial", "django"])


class Article(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    description = models.CharField(blank=True, verbose_name="Краткое описание")
    main_img = models.ImageField(upload_to='articles/%Y/%m', verbose_name='Главная картинка')
    content = models.TextField(blank=True, verbose_name="Текст статьи")
    author = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(choices=Status.choices, default=Status.DRAFT, verbose_name="Статус")
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='article', blank=True, verbose_name="Категории", )

    objects = models.Manager()
    published = PublishedManager()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create'])
        ]

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    icon = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})