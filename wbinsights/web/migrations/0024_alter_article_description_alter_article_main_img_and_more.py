# Generated by Django 5.0.3 on 2024-03-29 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0023_alter_article_description_alter_customuser_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='description',
            field=models.CharField(blank=True, verbose_name='Краткое описание'),
        ),
        migrations.AlterField(
            model_name='article',
            name='main_img',
            field=models.ImageField(upload_to='articles/%Y/%m', verbose_name='Главная картинка'),
        ),
        migrations.AlterField(
            model_name='expertprofile',
            name='about',
            field=models.CharField(max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='expertprofile',
            name='age',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='expertprofile',
            name='education',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='expertprofile',
            name='hour_cost',
            field=models.IntegerField(null=True),
        ),
    ]
