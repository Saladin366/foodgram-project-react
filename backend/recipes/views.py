from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from .models import Favorite, Ingredient, Recipe, Tag
from .permissions import IsAdminOrOwner
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeSerializer, TagSerializer)

RECIPE_IN_FAVORITES = 'Рецепт уже есть в избранном'
NOT_IN_FAVORITES = 'Рецепта нет в избранном'


class ListRetrieve(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    """Класс для получения списка или одного объекта."""
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

    @action(methods=('POST', 'DELETE'), detail=False,
            url_path=r'(?P<id>\d+)/favorite',
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        if request.method == 'DELETE':
            object = Favorite.objects.filter(recipe=recipe, user=user).first()
            if object is None:
                raise ValidationError(NOT_IN_FAVORITES)
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if Favorite.objects.filter(recipe=recipe, user=user).exists():
            raise ValidationError(RECIPE_IN_FAVORITES)
        serializer = FavoriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
