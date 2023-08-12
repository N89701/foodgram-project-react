from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('name', 'measurement_unit')
    list_editable = ('name', 'measurement_unit')
    list_display_links = None


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')
    list_display_links = None


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        field.name for field in Recipe._meta.fields if field.name != "id"
        ]
    search_fields = [
        field.name for field in Recipe._meta.fields if field.name != "id"
        ]
    list_filter = [
        field.name for field in Recipe._meta.fields if field.name != "id"
        ]
    list_editable = [
        field.name for field in Recipe._meta.fields if field.name != "id"
        ]
    inlines = [RecipeIngredientInline, ]
    empty_value_display = '-пусто-'
    list_display_links = None


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    list_display_links = None


class ShopingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    list_display_links = None


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShopingCartAdmin)
