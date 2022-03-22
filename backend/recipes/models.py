from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField('Название тега', unique=True, max_length=200)
    color = models.CharField('Цвет тега', unique=True, max_length=7)
    slug = models.SlugField('Уникальный слаг', unique=True, max_length=200)

    class Meta:
        ordering = ['id']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название', unique=True, max_length=200)
    measurement_unit = models.CharField('Единица измерения', max_length=200)

    class Meta:
        ordering = ['id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField('Название', max_length=200)
    text = models.TextField('Описание', max_length=200)
    image = models.ImageField('Картинка', upload_to='recipes/images/')
    cooking_time = models.IntegerField('Время приготовления (в минутах)')
    tags = models.ManyToManyField(Tag, related_name='recipes', null=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes')

    class Meta:
        ordering = ['id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    amount = models.IntegerField('Количество')
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='recipes')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='ingredients')


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='favorites')

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'recipe'], name='unique_favorite')
        ]
