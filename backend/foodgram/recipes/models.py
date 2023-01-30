from django.db import models

from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(max_length=7)
    slug = models.SlugField(unique=True, max_length=200)

    class Meta:
        verbose_name = 'Теги'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=10)

    class Meta:
        verbose_name = 'Ингредиенты'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        related_name='recipe_user',
        verbose_name='Автор рецепта',
        max_length=200,
        on_delete=models.CASCADE
        )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipe_tags',
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты рецепта',
        through='RecipeIngredient',
        related_name='recipe_ingredients',
    )
    name = models.CharField(max_length=200)
    text = models.TextField()
    cooking_time = models.PositiveSmallIntegerField()
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/images/',
        blank=True,
        help_text='Загрузите картинку рецепта'
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепты'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Наименование ингредиента',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Наименование рецепта',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент в рецептах'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def str(self):
        return f'Ингредиент: {self.ingredient} (Рецепт: {self.recipe})'


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shoppinglist",
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shoppinglist',
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        return self.recipe.name


class Favorite(models.Model):
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Пользователь избранного',
        related_name='user_favorite',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт избранного',
        related_name='recipe_favorite',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'Пользователь: {self.user} - Рецепт: {self.recipe}'


class Subscription(models.Model):
    follow = models.ForeignKey(
        CustomUser,
        verbose_name='Автор',
        related_name='follow_user',
        on_delete=models.CASCADE
    )
    follower = models.ForeignKey(
        CustomUser,
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        follow_name = (
            f'Автор: {self.follow.username} - ' +
            f'Подписчик: {self.follower.username}'
        )
        return follow_name
