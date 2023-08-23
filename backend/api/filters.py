from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from kitchen.models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    is_favorited = filters.BooleanFilter(method='is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart')

    def is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_cart__user=user)
        return queryset
    
    class Meta:
        model = Recipe
        fields = ('tags', 'author',)


class IngredientTypeFilter(SearchFilter):
    search_param = 'name'
