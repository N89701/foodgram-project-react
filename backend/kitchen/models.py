from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, RegexValidator

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        max_length=settings.LENGTH_LIMITS['ingredient_name']
    )
    measurement_unit = models.CharField(
        max_length=settings.LENGTH_LIMITS['ingredient_measurement_unit']
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Tag(models.Model):
    name = models.CharField(max_length=settings.LENGTH_LIMITS['tag_name'])
    color = models.CharField(
        max_length=7,
        validators=[
            RegexValidator(
                '^#([a-fA-F0-9]{6})',
                message='Введите # и 6 символов(цифры и латинские буквы)'
            )
        ]
    )
    slug = models.SlugField(
        unique=True,
        max_length=settings.LENGTH_LIMITS['tag_slug']
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=settings.LENGTH_LIMITS['recipe_name'])
    image = models.ImageField(upload_to='pictures/')
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-pub_date',)


class RecipeIngredient(models.Model):
    name = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        ordering = ('recipe',)
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'recipe'),
                name='no double ingredient for one recipe'
            ),
        )
        default_related_name = 'recipeingredients'

    def __str__(self):
        return f'{self.name}, {self.amount}{self.name.measurement_unit}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='admirers'
    )

    class Meta:
        ordering = ('user', 'recipe')
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='no double favorites'
            ),
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_carts'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='buyers'
    )

    class Meta:
        ordering = ('user', 'recipe')
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='no double buy'
            ),
        )
