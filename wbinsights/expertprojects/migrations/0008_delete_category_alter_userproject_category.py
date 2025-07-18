# Generated by Django 5.0.2 on 2024-04-30 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expertprojects', '0007_alter_userproject_members'),
        ('web', '0036_alter_customuser_email_alter_customuser_phone_number'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Category',
        ),
        migrations.AlterField(
            model_name='userproject',
            name='category',
            field=models.ManyToManyField(related_name='userprojects', to='web.category', verbose_name='Категории'),
        ),
    ]
