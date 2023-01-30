from django.shortcuts import get_object_or_404
from django.http.response import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes

from api.permissions import OwnerAdminOrReadOnly
from api.filters import RecipeFilter

from recipes.models import (
    Tag,
    Ingredient,
    RecipeIngredient,
    Recipe,
    Favorite,
    ShoppingCart,
)

from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeReadSerializer,
    SubcriptionRecipeSerializer,
    ShoppingCartSerializer,
    FavoriteSerializer
)

from users.models import CustomUser


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ['get']
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny, )

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get("name")
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (OwnerAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        queryset = Recipe.objects.all()
        is_favorited = self.request.query_params.get("is_favorited")
        is_in_shopping_cart = self.request.query_params.get(
            "is_in_shopping_cart"
        )
        all_cart = ShoppingCart.objects.filter(user=self.request.user.id)
        all_favorite = Favorite.objects.filter(user=self.request.user.id)

        if is_favorited == '1':
            queryset = queryset.filter(recipe_favorite__in=all_favorite)
        if is_favorited == '0':
            queryset = queryset.exclude(recipe_favorite__in=all_favorite)

        if is_in_shopping_cart == '1':
            queryset = queryset.filter(shoppinglist__in=all_cart)
        if is_in_shopping_cart == '0':
            queryset = queryset.exclude(shoppinglist__in=all_cart)

        return queryset.all()

    @action(
        methods=["POST", "DELETE"],
        url_path='favorite',
        url_name='favorite',
        permission_classes=[IsAuthenticated],
        detail=True
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = get_object_or_404(CustomUser, id=request.user.id)

        serializer = FavoriteSerializer(
            data={'user': user.id, 'recipe': recipe.id}
        )

        if request.method == "POST":
            if Favorite.objects.filter(recipe=recipe, user=user).exists():
                return Response(
                    f'Recipe -- {recipe} -- already in favorites for user: '
                    f'{user}', status=status.HTTP_400_BAD_REQUEST
                )
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, user=user)
            serializer = SubcriptionRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not Favorite.objects.filter(recipe=recipe, user=user).exists():
            return Response(
                f'Recipe -- {recipe} -- not in favorites for user: '
                f'{user}. Can not delete',
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite = get_object_or_404(Favorite, user=user, recipe__id=pk)
        favorite.delete()
        return Response(
            f'Recipe -- {recipe} -- removed from favorites for user: '
            f'{user}', status=status.HTTP_204_NO_CONTENT
        )

    @action(
        methods=["POST", "DELETE"],
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=[IsAuthenticated],
        detail=True
    )
    def shopping_card(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = get_object_or_404(CustomUser, id=request.user.id)

        serializer = ShoppingCartSerializer(
            data={'user': user.id, 'recipe': recipe.id}
        )

        if request.method == "POST":
            if ShoppingCart.objects.filter(recipe=recipe, user=user).exists():
                return Response(
                    f'Recipe -- {recipe} - already in shopping card for user: '
                    f'{user}', status=status.HTTP_400_BAD_REQUEST
                )
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, user=user)
            serializer = SubcriptionRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not ShoppingCart.objects.filter(recipe=recipe, user=user).exists():
            return Response(
                f'Recipe -- {recipe} -- not in shopping card for user: '
                f'{user}. Can not delete',
                status=status.HTTP_400_BAD_REQUEST
            )
        in_list = get_object_or_404(ShoppingCart, user=user, recipe__id=pk)
        in_list.delete()
        return Response(
            f'Recipe -- {recipe} -- removed from shopping card for user: '
            f'{user}', status=status.HTTP_204_NO_CONTENT
        )

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeSerializer


@api_view(['GET', ])
@permission_classes([IsAuthenticated])
def download_shopping_cart(request):
    user = request.user
    shopping_list = user.shoppinglist.all()

    buy_list = {}

    for item in shopping_list:
        recipe = item.recipe
        ingredients = recipe.ingredients.all()
        for ingredient in ingredients:
            amount = RecipeIngredient.objects.get(
                recipe=recipe,
                ingredient=ingredient
            ).amount
            if buy_list.get(ingredient):
                buy_list[ingredient] += amount
            else:
                buy_list[ingredient] = amount

    result, counter = [], 0
    for ing, am in buy_list.items():
        counter += 1
        line = f'{counter}) {ing.name} - {am} {ing.measurement_unit}\n'
        result.append(line)

    response = HttpResponse(result, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=shopping_list.txt'
    return response
