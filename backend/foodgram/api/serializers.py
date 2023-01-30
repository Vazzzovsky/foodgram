from django.shortcuts import get_object_or_404

from rest_framework import serializers
from drf_base64.fields import Base64ImageField

from users.serializers import UserSerializer
from users.models import CustomUser

from recipes.models import (
    Tag,
    Ingredient,
    RecipeIngredient,
    Recipe,
    Favorite,
    ShoppingCart,
    Subscription,
)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    recipe = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Favorite
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    name = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='name',
        read_only=True
    )
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='measurement_unit',
        read_only=True,
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeIngredientSerializerCreate(RecipeIngredientSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.FloatField(write_only=True)


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = UserSerializer(read_only=True)
    image = Base64ImageField(max_length=None, use_url=True)
    ingredients = RecipeIngredientSerializerCreate(many=True)

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_is_favorited(self, obj):
        current_user = self.context.get('request').user
        current_recipe = obj
        is_favorite = Favorite.objects.filter(
            user=current_user,
            recipe=current_recipe
        ).exists()
        return is_favorite

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context.get('request').user
        current_recipe = obj
        in_cart = ShoppingCart.objects.filter(
            user=current_user,
            recipe=current_recipe
        ).exists()
        return in_cart

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)

        objs = []
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            ingredient_instance = get_object_or_404(
                Ingredient,
                pk=ingredient.get('id')
            )
            objs.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient_instance,
                    amount=amount
                )
            )
        RecipeIngredient.objects.bulk_create(objs)

        recipe.save()
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.filter(id=instance.id)
        recipe.update(**validated_data)
        ingredients_instance = [
            ingredient for ingredient in instance.ingredients.all()
        ]
        for item in ingredients:
            amount = item['amount']
            ingredient_id = item['id']
            if RecipeIngredient.objects.filter(
                    id=ingredient_id,
                    amount=amount
            ).exists():
                ingredients_instance.remove(
                    RecipeIngredient.objects.get(
                        id=ingredient_id,
                        amount=amount
                    ).ingredient)
            else:
                RecipeIngredient.objects.get_or_create(
                    recipe=instance,
                    ingredient=get_object_or_404(Ingredient, id=ingredient_id),
                    amount=amount
                )
        if validated_data.get('image') is not None:
            instance.image = validated_data.get('image', instance.image)
        instance.ingredients.remove(*ingredients_instance)
        instance.tags.set(tags)
        return instance

    def validate(self, attrs):
        if len(attrs["tags"]) == 0:
            raise serializers.ValidationError("Не выбранор ни одного тега")
        if len(attrs["tags"]) != len(set(attrs["tags"])):
            raise serializers.ValidationError("Теги должны быть уникальны")
        if len(attrs["ingredientinrecipe_set"]) == 0:
            raise serializers.ValidationError(
                "Не выбрано ни одного ингредиента"
            )
        ingredients = attrs["ingredientinrecipe_set"]
        if len(ingredients) != len(set(obj["ingredient"] for obj in ingredients)):
            raise serializers.ValidationError("Ингредиенты должны быть уникальны")
        if any(obj["amount"] <= 0 for obj in ingredients):
            raise serializers.ValidationError(
                "Нет количества ингредиентов"
            )
        if attrs["cooking_time"] <= 0:
            raise serializers.ValidationError(
                "Укажите время приготовления"
            )
        return super().validate(attrs)


class SubcriptionRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    recipe = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ShoppingCart
        fields = '__all__'


class RecipeReadSerializer(RecipeSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set',
        many=True,
    )


class SubscribeUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = SubcriptionRecipeSerializer(
        source='recipe_user',
        many=True
    )
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]

    def get_is_subscribed(self, obj):
        current_user = self.context.get('current_user')
        current_recipe_author = obj
        is_subscribed = Subscription.objects.filter(
            follow=current_recipe_author,
            follower=current_user
        ).exists()
        return is_subscribed

    def get_recipes_count(self, obj):
        current_recipe_author = obj
        amount = Recipe.objects.filter(author=current_recipe_author).count()
        return amount


class SubscribeSerializer(serializers.ModelSerializer):
    follow = serializers.StringRelatedField(read_only=True)
    follower = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Subscription
        fields = '__all__'
