from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from .filters import RecipeFilter
from .models import Cart, Favorite, Ingredient, Recipe, Tag
from .permissions import IsAdminOrOwner
from .serializers import (CartSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeSerializer,
                          TagSerializer)

RECIPE_IN_FAVORITES = 'Рецепт уже есть в избранном'
NOT_IN_FAVORITES = 'Рецепта нет в избранном'
RECIPE_IN_CART = 'Рецепт уже есть в корзине'
NOT_IN_CART = 'Рецепта нет в корзине'


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
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrOwner)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def favorite_or_cart(self, request, id, model, mes_not_in, mes_in, ser):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        if request.method == 'DELETE':
            object = model.objects.filter(recipe=recipe, user=user).first()
            if object is None:
                raise ValidationError(mes_not_in)
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if model.objects.filter(recipe=recipe, user=user).exists():
            raise ValidationError(mes_in)
        serializer = ser(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=('POST', 'DELETE'), detail=False,
            url_path=r'(?P<id>\d+)/favorite',
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, id):
        return self.favorite_or_cart(request, id, Favorite, NOT_IN_FAVORITES,
                                     RECIPE_IN_FAVORITES, FavoriteSerializer)

    @action(methods=('POST', 'DELETE'), detail=False,
            url_path=r'(?P<id>\d+)/shopping_cart',
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, id):
        return self.favorite_or_cart(request, id, Cart, NOT_IN_CART,
                                     RECIPE_IN_CART, CartSerializer)

    @action(detail=False)
    def download_shopping_cart(self, request):
        return Response('Ok')
