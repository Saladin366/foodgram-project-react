from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .models import Favorite, Ingredient, Recipe, Tag
from .permissions import IsAdminOrOwner
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, TagSerializer)


class ListRetrieve(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    """Класс для получения списка или одного объекта."""
    pass


class CreateDestroy(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """Класс для создания или удаления объекта."""
    pass


class TagViewSet(ListRetrieve):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(ListRetrieve):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrOwner)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class FavoriteViewSet(CreateDestroy):
    """Viewset для модели Favorite."""
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)

    # def get_queryset(self):
    #     recipe_id = self.kwargs.get("id")
    #     recipe = get_object_or_404(Recipe, id=recipe_id)
    #     return Favorite.objects

    # def perform_create(self, serializer):
    #     post_id = self.kwargs.get("post_id")
    #     post = get_object_or_404(Post, id=post_id)
    #     serializer.save(author=self.request.user, post=post)