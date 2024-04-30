from django.contrib import admin

from .forms import UserProjectForm
from .models import UserProject, UserProjectCustomer


class UserProjectAdmin(admin.ModelAdmin):
    form = UserProjectForm
    list_display = ('name', 'display_categories', 'customer', 'year', 'time_create', 'time_update')
    list_filter = ('time_create', 'customer', 'year', 'category')
    search_fields = ('name', 'goals', 'key_results')
    prepopulated_fields = {"slug": ("name",)}
    ordering = ('-time_create',)

    def display_categories(self, obj):
        """Функция для отображения категорий в List display."""
        return ', '.join([category.name for category in obj.category.all()[:3]])  # Отображаем до 3-х категорий
    display_categories.short_description = 'Категории'


admin.site.register(UserProject, UserProjectAdmin)


class UserProjectCustomerAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(UserProjectCustomer, UserProjectCustomerAdmin)
