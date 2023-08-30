from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from kitchen.models import Recipe, Tag


class RecipeFilter(FilterSet):
    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(admirers__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(buyers__user=user)
        return queryset


class IngredientTypeFilter(SearchFilter):
    search_param = 'name'
