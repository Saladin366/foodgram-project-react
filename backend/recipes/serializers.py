import base64
import uuid

from django.core.files.base import ContentFile
from django.shortcuts import get_list_or_404
from rest_framework import serializers

from users.serializers import UserSerializer
from .models import Favorite, Ingredient, Recipe, RecipeIngredient, Tag

INGREDIENS_KEY_ERROR = 'Поле ingredients обязательно'
INGREDIENT_NOT_CORRECT = 'Каждый ингредиент должен содержать поля : id, amount'
INGREDIENT_NOT_FOUND = 'Ингредиент с id = {} не существует'
SAME_INGREDIENT = 'Ингредиент с id = {} добавлен дважды'
TAGS_KEY_ERROR = 'Поле tags обязательно'
TAG_NOT_FOUND = 'Тег с id = {} не существует'
RECIPE_IN_FAVORITES = 'Рецепт уже есть в избранном'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class Base64ToFile(serializers.ImageField):
    def to_internal_value(self, data):
        format, datastr = data.split(';base64,')
        ext = format.split('/')[-1]
        if ext[:3] == 'svg':
            ext = 'svg'
        return ContentFile(
            base64.b64decode(datastr), name='{}.{}'.format(uuid.uuid4(), ext))


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(many=True, read_only=True)
    image = Base64ToFile()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        return False

    def get_is_in_shopping_cart(self, obj):
        return False

    def list_ingredients(self, initial_data):
        ingredients_id = initial_data.pop('ingredients', None)
        if ingredients_id is None:
            raise serializers.ValidationError(INGREDIENS_KEY_ERROR)
        ingredients = []
        ids = set()
        for ingredient_id in ingredients_id:
            id = ingredient_id.get('id', None)
            amount = ingredient_id.get('amount', None)
            if id is None or amount is None:
                raise serializers.ValidationError(INGREDIENT_NOT_CORRECT)
            if id in ids:
                raise serializers.ValidationError(SAME_INGREDIENT.format(id))
            ids.add(id)
            ingredient = Ingredient.objects.filter(id=id).first()
            if ingredient is None:
                raise serializers.ValidationError(
                    INGREDIENT_NOT_FOUND.format(id))
            ingredients.append((ingredient, amount))
        return ingredients

    def list_tags(self, initial_data):
        tags_id = self.initial_data.pop('tags', None)
        if tags_id is None:
            raise serializers.ValidationError(TAGS_KEY_ERROR)
        tags = []
        for id in tags_id:
            tag = Tag.objects.filter(id=id).first()
            if tag is None:
                raise serializers.ValidationError(TAG_NOT_FOUND.format(id))
            tags.append(tag)
        return tags

    def create(self, validated_data):
        ingredients = self.list_ingredients(self.initial_data)
        tags = self.list_tags(self.initial_data)
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        recipe.save()
        for ingredient, amount in ingredients:
            RecipeIngredient.objects.create(
                amount=amount, ingredient=ingredient, recipe=recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = self.list_ingredients(self.initial_data)
        tags = self.list_tags(self.initial_data)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.tags.set(tags)
        instance.save()
        recipeingredients = get_list_or_404(RecipeIngredient, recipe=instance)
        for object in recipeingredients:
            object.delete()
        for ingredient, amount in ingredients:
            RecipeIngredient.objects.create(
                amount=amount, ingredient=ingredient, recipe=instance)
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ReadOnlyField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('name', 'owner'),
                message=RECIPE_IN_FAVORITES)
        ]
