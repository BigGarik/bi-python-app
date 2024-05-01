import logging

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.urls import reverse

from web.models import Category

logger = logging.getLogger(__name__)


class UserProject(models.Model):
    author = models.ForeignKey('web.CustomUser', on_delete=models.CASCADE, related_name="userproject",
                               verbose_name="Автор")
    members = models.ManyToManyField('web.CustomUser', related_name='userprojects', verbose_name="Участники")
    name = models.CharField(max_length=255, verbose_name=_("Heading"))
    category = models.ManyToManyField(Category, related_name='userprojects', verbose_name=_("Category"))
    key_results = ArrayField(models.CharField(max_length=200), blank=True, verbose_name="Результаты")
    customer = models.ForeignKey('UserProjectCustomer', on_delete=models.SET_NULL, null=True,
                                 related_name="userproject", verbose_name="Заказчик")
    year = models.IntegerField(verbose_name="Год")
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


def validate_file_extension(value):
    if not value.name.lower().endswith(('.pdf', '.doc', '.docx', '.odt', '.txt', '.xlsx', '.xls')):
        raise ValidationError(_('Unsupported file extension.'))


class UserProjectFile(models.Model):
    file = models.FileField(upload_to="expert/projects/%Y/%m/%d/", validators=[validate_file_extension])
    project = models.ForeignKey('UserProject', related_name='files', on_delete=models.CASCADE)

    def __str__(self):
        return f"File for {self.project}"


class UserProjectCustomer(models.Model):
    name = models.CharField(max_length=255, verbose_name="Наименование")

    def __str__(self):
        return self.name
