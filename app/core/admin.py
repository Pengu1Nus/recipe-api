"""
Кастомизация админки.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


class UserAdmin(BaseUserAdmin):
    """Определение админки."""

    ordering = ('id',)
    list_display = ('username', 'name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (
            _('Разрешения'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            },
        ),
        (_('Временные метки'), {'fields': ('last_login',)}),
    )
    readonly_fields = ('last_login',)
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'password1',
                    'password2',
                    'name',
                    'is_active',
                    'is_staff',
                    'is_superuser',
                ),
            },
        ),
    )


class RecipeAdmin(admin.ModelAdmin):
    autocomplete_fields = ('ingredients',)


class IngredientAdmin(admin.ModelAdmin):
    list_per_page = 10
    ordering = ('name',)
    search_fields = ('name',)


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.Tag)
admin.site.register(models.Ingredient, IngredientAdmin)
