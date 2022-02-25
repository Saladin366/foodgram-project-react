from django.contrib import admin

from .models import Ingredient, Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
