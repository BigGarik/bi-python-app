from django.db import models
from django.urls import reverse


class Image(models.Model):
    image = models.ImageField(upload_to='images/%Y/%m/%d/')
    article = models.ForeignKey('Article', related_name='image', on_delete=models.CASCADE)

    def __str__(self):
        return f"Image for {self.article}"


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    icon = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})
