# isort: skip_file
from django.contrib import admin
from django.utils.text import Truncator

from .models import Cart, Favorite, Ingredient, ReciIngredi, Recipe, Tag


class ReciIngrediInline(admin.TabularInline):
    model = ReciIngredi
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_display_links = ('name',)
    list_filter = ('name',)
    inlines = (ReciIngrediInline,)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'name', 'short_text', 'total_faved')
    list_display_links = ('name',)
    list_filter = ('tags', 'author', 'name')
    empty_value_display = '-/-'
    inlines = (ReciIngrediInline,)

    @admin.display(description='Name')
    def tags(self, obj):
        return Tag.recipes.object.filter(recipe=obj.pk)

    def total_faved(self, obj):
        return obj.faved_by.count()

    def short_text(self, obj):
        return Truncator(obj.text).chars(120)
    short_text.short_description = 'Текст'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    list_display_links = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe', 'recipe_id')
    search_fields = ('user', 'recipe',)
    list_filter = ('user',)

    def recipe_id(self, fav):
        return fav.recipe.id


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe',)
    list_filter = ('user',)
