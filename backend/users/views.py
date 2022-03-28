from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from .models import Subscription, User
from .serializers import (CreateUserSerializer, SubscribeSerializer,
                          UserSerializer)

SUBSCRIBE_EXIST = 'Вы уже подписаны на данного автора'
SUBSCRIBE_NOT_EXIST = 'Вы не подписаны на данного автора'
SUBSCRIBE_TO_MYSELF = 'Нельзя подписать на самого себя'


class CreateListRetrieve(mixins.CreateModelMixin, mixins.ListModelMixin,
                         mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Класс для получения списка объектов, создания или получения объекта."""
    pass


class UserViewSet(CreateListRetrieve):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.action == 'create' or self.action == 'list':
            return (AllowAny(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.action == 'subscribe' or self.action == 'subscriptions':
            return SubscribeSerializer
        return UserSerializer

    @action(detail=False)
    def me(self, request):
        user = get_object_or_404(User, username=request.user.username)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(methods=('POST',), detail=False)
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(
            serializer.validated_data['new_password'])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=('POST', 'DELETE'), detail=False,
            url_path=r'(?P<id>\d+)/subscribe')
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            raise ValidationError(SUBSCRIBE_TO_MYSELF)
        if request.method == 'DELETE':
            object = Subscription.objects.filter(
                author=author, user=user).first()
            if object is None:
                raise ValidationError(SUBSCRIBE_NOT_EXIST)
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if Subscription.objects.filter(author=author, user=user).exists():
            raise ValidationError(SUBSCRIBE_EXIST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False)
    def subscriptions(self, request):
        objects = Subscription.objects.filter(user=request.user)
        if not objects:
            return Response(status=status.HTTP_200_OK)
        page = self.paginate_queryset(objects)
        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(objects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
