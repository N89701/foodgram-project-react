from django.core.validators import MinValueValidator
from django.db import transaction
from django.db.models import F
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField, ValidationError)

from API.v1.users.serializers import CustomUserSerializer
from kitchen.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientsCUDSerializer(ModelSerializer):
    id = IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeInFollowSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(RecipeInFollowSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

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

    def get_is_favorited(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Favorite.objects.filter(
                user=self.context.get('request').user,
                recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and ShoppingCart.objects.filter(
                user=self.context.get('request').user,
                recipe=obj).exists()
        )

    def get_ingredients(self, recipe):
        return recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipeingredient__amount')
        )


class RecipeCUDSerializer(RecipeInFollowSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = RecipeIngredientsCUDSerializer(many=True)
    cooking_time = IntegerField(validators=(MinValueValidator(
        1,
        message='Время приготовления не менее 1 минуты'
    ),))

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate(self, obj):
        if not obj.get('tags'):
            raise ValidationError(
                'Укажите тег(и)'
            )
        if not obj.get('ingredients'):
            raise ValidationError(
                'Укажите ингредиент(ы)'
            )
        ingredients = [
            elem['id'] for elem in self.initial_data.get('ingredients')
        ]
        tags = list(self.initial_data.get('tags'))
        if len(set(ingredients)) != len(ingredients):
            raise ValidationError(
                'Ингредиенты не должны повторяться'
            )
        if len(set(tags)) != len(tags):
            raise ValidationError(
                'Теги не должны повторяться'
            )
        return obj

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.recipe_ingredient_create(ingredients, RecipeIngredient, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        if 'tags' in self.validated_data:
            tags_data = validated_data.pop('tags')
            instance.tags.set(tags_data)
        if 'ingredients' in self.validated_data:
            ingredients = validated_data.pop('ingredients')
            amount_set = RecipeIngredient.objects.filter(
                recipe__id=instance.id)
            amount_set.delete()
            self.recipe_ingredient_create(
                ingredients,
                RecipeIngredient,
                instance
            )
        return super().update(instance, validated_data)

    def recipe_ingredient_create(self, ingredients, model, recipe):
        model.objects.bulk_create(
            model(
                recipe=recipe,
                name_id=ingredient['id'],
                amount=ingredient['amount'])
            for ingredient in ingredients
        )

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data
