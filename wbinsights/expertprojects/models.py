from django.contrib.postgres.fields import ArrayField
from django.db import models
from web.models.users import CustomUser
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    icon = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})


class UserProject(models.Model):
    member = models.ForeignKey('web.CustomUser', on_delete=models.SET_NULL, null=True, related_name="userproject")
    name = models.CharField(max_length=255, verbose_name="Заголовок")
    category = models.ManyToManyField('Category', related_name='userprojects', blank=True, verbose_name="Категории")
    key_results = ArrayField(models.CharField(max_length=200), blank=True)  # Текст через запятую
    customer = models.ForeignKey('UserProjectCustomer', on_delete=models.SET_NULL, null=True, related_name="userproject")
    year = models.IntegerField()
    goals = models.TextField(blank=True, verbose_name="Текст проекта")
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-time_create']
        indexes = [
            models.Index(fields=['-time_create'])
        ]

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'slug': self.slug})


class UserProjectFile(models.Model):
    file = models.FileField(upload_to="expertprojects/%Y/%m/%d/")
    project = models.ForeignKey('UserProject', related_name='userprojectfile', on_delete=models.CASCADE)

    def __str__(self):
        return f"File for {self.project}"


class UserProjectCustomer(models.Model):
    name = models.CharField(max_length=255, verbose_name="Наименование")

    def __str__(self):
        return self.name
