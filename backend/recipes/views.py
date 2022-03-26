from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from .filters import RecipeFilter
from .models import Cart, Favorite, Ingredient, Recipe, RecipeIngredient, Tag
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

    def favorite_or_cart(self, request, id, model, message_not_in, message_in,
                         class_serializer):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        if request.method == 'DELETE':
            object = model.objects.filter(recipe=recipe, user=user).first()
            if object is None:
                raise ValidationError(message_not_in)
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if model.objects.filter(recipe=recipe, user=user).exists():
            raise ValidationError(message_in)
        serializer = class_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        cart = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user).values(
                'ingredient__name', 'ingredient__measurement_unit').annotate(
                    count=Sum('amount'))
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="cart.txt"'
        for ingredient in cart:
            row = '{} - {} {}\n'.format(
                ingredient['ingredient__name'],
                ingredient['count'],
                ingredient['ingredient__measurement_unit'])
            response.write(row)
        return response
