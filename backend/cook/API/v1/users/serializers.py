from rest_framework import serializers
from djoser.serializers import UserSerializer
from users.models import User, Follow


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name', 'email', 'is_subscribed')

    def get_is_subscribed(self, obj):
        if self.context.get('request').user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=self.context.get('request').user,
            author=obj
        ).exists()


class FollowSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(
        source='follows.author.recipes.count'
    )

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_recipes(self, obj, recipes_limit=None):
        from API.v1.kitchen.serializers import RecipeInFollowSerializer
        if self.context.get('request').query_params.get('recipes_limit'):
            recipes_limit = int(self.context.get(
                'request'
            ).query_params.get('recipes_limit'))
        recipes = obj.recipes.all()[:recipes_limit]
        serializer = RecipeInFollowSerializer(recipes, many=True)
        return serializer.data
