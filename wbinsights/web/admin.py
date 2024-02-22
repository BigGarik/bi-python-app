from django.contrib import admin
from .models import Article, Category, Image


class ImageAdmin(admin.ModelAdmin):
    list_display = ('image', 'article',)


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'slug', 'is_published', 'cat',)
    prepopulated_fields = {'slug': ('title',)}


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Image, ImageAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Category, CategoryAdmin)
