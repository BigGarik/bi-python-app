# Generated by Django 5.0.2 on 2024-04-08 10:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expertprojects', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='userproject',
            name='member',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='userproject', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='UserProjectMember',
        ),
    ]
