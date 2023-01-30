from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    download_shopping_cart,
)

from users.views import CustomUserViewSet


app_name = 'api'

router = SimpleRouter()

router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path(
        r'recipes/download_shopping_cart/',
        download_shopping_cart,
        name="download_shopping_cart",
    ),
    path('', include(router.urls)),
    path(
        r'users/subscriptions/',
        CustomUserViewSet.as_view({"get": "subscribe_list"}),
        name="subscriptions",
    ),
    path(
        r'users/<int:pk>/subscribe/',
        CustomUserViewSet.as_view(
            {"post": "subscribe", "delete": "subscribe"}
        ),
        name="subscribe",
    ),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
