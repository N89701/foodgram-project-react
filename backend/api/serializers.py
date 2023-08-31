from django.core.validators import MinValueValidator
from django.db import transaction
from django.db.models import F
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (
    BooleanField, IntegerField, ModelSerializer, PrimaryKeyRelatedField,
    SerializerMethodField, ValidationError
)
from rest_framework.validators import UniqueTogetherValidator
from rest_framework import status

from kitchen.models import (
    Favorite, Ingredient, Recipe,
    RecipeIngredient, ShoppingCart, Tag
)
from users.models import Follow, User


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name', 'email', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (
            request and request.user.is_authenticated
            and obj.followers.filter(user=request.user).exists()
        )


class FollowSerializer(CustomUserSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_recipes(self, obj, recipes_limit=None):
        recipes = obj.recipes.all()
        request = self.context.get('request')
        if request.query_params.get('recipes_limit'):
            recipes_limit = int(request.query_params.get('recipes_limit'))
            recipes = recipes[:recipes_limit]
        serializer = RecipeInFollowSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FollowCreateSerializer(ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'author'],
                message='Вы уже подписаны на этого пользователя!'
            )
        ]

    def validate(self, data):
        author = data.get('author')
        user = data.get('user')
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientsCUDSerializer(ModelSerializer):
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = IntegerField(validators=(MinValueValidator(
        1,
        message='Ингредиента должно быть больше 1'
    ),))

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeInFollowSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(RecipeInFollowSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = SerializerMethodField()
    is_favorited = BooleanField(read_only=True)
    is_in_shopping_cart = BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_ingredients(self, recipe):
        return recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipeingredients__amount')
        )


class RecipeCUDSerializer(RecipeInFollowSerializer):
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = RecipeIngredientsCUDSerializer(many=True)
    cooking_time = IntegerField(validators=(MinValueValidator(
        1,
        message='Время приготовления не менее 1 минуты'
    ),))
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate_tags(self, value):
        if not value:
            raise ValidationError('Укажите тег(и)')
        if len(set(value)) != len(value):
            raise ValidationError('Теги не должны повторяться')
        return value

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError('Укажите ингредиент(ы)')
        ingredients = [elem['id'] for elem in value]
        if len(set(ingredients)) != len(ingredients):
            raise ValidationError('Ингредиенты не должны повторяться')
        return value

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context.get('request').user
        )
        recipe.tags.set(tags)
        self.recipe_ingredient_create(ingredients, RecipeIngredient, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        instance.tags.set(tags_data)
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        self.recipe_ingredient_create(
            ingredients,
            RecipeIngredient,
            instance
        )
        return super().update(instance, validated_data)

    @staticmethod
    def recipe_ingredient_create(ingredients, model, recipe):
        model.objects.bulk_create(
            model(
                recipe=recipe,
                name=ingredient['id'],
                amount=ingredient['amount'])
            for ingredient in ingredients
        )

    def to_representation(self, instance):
        user = self.context.get('request').user
        instance.is_favorited = user.favorites.filter(
            recipe=instance
        ).exists()
        instance.is_in_shopping_cart = user.shopping_carts.filter(
            recipe=instance
        ).exists()
        return RecipeSerializer(instance, context=self.context).data


class ShoppingCartSerializer(ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['user', 'recipe'],
                message='Рецепт уже добавлен в корзину'
            )
        ]


class FavoriteSerializer(ModelSerializer):
    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe'],
                message='Рецепт уже добавлен в избранное'
            )
        ]
