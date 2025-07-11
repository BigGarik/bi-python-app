# Generated by Django 5.0.4 on 2024-05-03 07:13

import django.contrib.postgres.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expertprojects', '0008_delete_category_alter_userproject_category'),
        ('web', '0037_article_allow_comments'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='userproject',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userproject', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='userproject',
            name='category',
            field=models.ManyToManyField(related_name='userprojects', to='web.category', verbose_name='Category'),
        ),
        migrations.AlterField(
            model_name='userproject',
            name='customer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='userproject', to='expertprojects.userprojectcustomer', verbose_name='Заказчик'),
        ),
        migrations.AlterField(
            model_name='userproject',
            name='key_results',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, size=None, verbose_name='Результаты'),
        ),
        migrations.AlterField(
            model_name='userproject',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Heading'),
        ),
        migrations.AlterField(
            model_name='userproject',
            name='year',
            field=models.IntegerField(verbose_name='Год'),
        ),
    ]
