# Generated by Django 5.0.2 on 2024-02-27 12:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0010_rename_tagpost_tagarticle_article_tags'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TagArticle',
            new_name='Tags',
        ),
    ]
