from datetime import datetime

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import exceptions, status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.pagination import LimitPageNumberPagination
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.filters import RecipeFilter, SearchFilter
from api.serializers import (IngredientSerializer, RecipeCUDSerializer,
                             RecipeInFollowSerializer, FollowCreateSerializer,
                             TagSerializer, FollowSerializer, RecipeSerializer,
                             ShoppingCartSerializer, FavoriteSerializer)
from kitchen.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import User, Follow


class TagViewSet(ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('name', )


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = LimitPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCUDSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.create_object(FavoriteSerializer, pk, request)
        return self.delete_object(Favorite, request.user, pk)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.create_object(ShoppingCartSerializer, pk, request)
        return self.delete_object(ShoppingCart, request.user, pk)

    def create_object(self, serializer, pk, request):
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_object(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.delete()[0]:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, **kwargs):
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__shoppingcart__user=request.user)
            .values('name')
            .annotate(total_amount=Sum('amount'))
            .values_list('name__name', 'total_amount',
                         'name__measurement_unit')
        )
        file_list = []
        [file_list.append(
            '{}. {} - {}{}.'.format(count, *ingredient))
            for count, ingredient in enumerate(ingredients, 1)]
        return HttpResponse(f'Cписок покупок на {datetime.now().date()}:\n'
                            + '\n'.join(file_list),
                            content_type='attachment/pdf')


class CustomUserViewSet(UserViewSet):
    pagination_class = LimitPageNumberPagination

    @action(
        detail=True,
        permission_classes=(IsAuthenticated,),
        methods=['POST', 'DELETE']
    )
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = FollowCreateSerializer(
                data={
                    'user': user.id,
                    'author': author.id
                },
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        unfollow = Follow.objects.filter(user=user, author=author).delete()
        if unfollow[0]:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        methods=['GET']
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(followers__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
