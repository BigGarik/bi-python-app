from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Article, Category, CustomUser, Research, QuestionAnswer
from .models.users import ExpertProfile
from .views import CustomUserCreationForm
from .views.profile import CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["email", "username", "is_active", "profile"]


admin.site.register(CustomUser, CustomUserAdmin)


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_description', 'slug', 'is_published', 'cat', 'author')
    prepopulated_fields = {'slug': ('title',)}

    def short_description(self, obj):
        return obj.content[:250]  # Возвращает первые 50 символов поля content

    short_description.short_description = "Краткое содержание"  # задает заголовок столбца


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


@admin.register(ExpertProfile)
class ExpertProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified')
    list_filter = ('is_verified',)
    actions = ['make_verified']

    def make_verified(self, request, queryset):
        queryset.update(is_verified=ExpertProfile.ExpertVerifiedStatus.VERIFIED)
    make_verified.short_description = "Mark selected experts as verified"