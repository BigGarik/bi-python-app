from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Article, Category, CustomUser, Research, QuestionAnswer
from .views import CustomUserCreationForm
from .views.profile import CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["email", "username", "is_active", "profile"]


admin.site.register(CustomUser, CustomUserAdmin)


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'slug', 'is_published', 'cat','author')
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Article, ArticleAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Category, CategoryAdmin)


class ResearchAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Research, ResearchAdmin)


class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug',)
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(QuestionAnswer, QuestionAnswerAdmin)
