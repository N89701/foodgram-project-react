from djoser.views import UserViewSet
from rest_framework import exceptions, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from API.pagination import MyPaginator
from API.v1.users.serializers import FollowSerializer
from users.models import User, Follow



class CustomUserViewSet(UserViewSet):
    pagination_class = MyPaginator

    @action(
        detail=True,
        permission_classes=(IsAuthenticated,),
        methods=['POST', 'DELETE']
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if user == author:
                raise exceptions.ValidationError(
                    'Самоподписка запрещена!'
                )
            if Follow.objects.filter(user=user, author=author).exists():
                raise exceptions.ValidationError(
                    'Вы уже подписаны на данного пользователя'
                )
            Follow.objects.create(user=user, author=author)
            serializer = FollowSerializer(
                author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(Follow, user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
