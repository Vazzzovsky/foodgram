from django.contrib import admin
from .models import (
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
    Ingredient,
    Favorite,
    Subscription,
)


class IngredientInRecipeInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    @admin.display(description="Количество добавлений в избранное")
    def favorite_amount(self):
        return Favorite.objects.filter(recipe=self.id).count()

    @admin.display(description="Теги рецепта")
    def tags_line(self):
        return ", ".join(map(str, self.tags.all()))

    list_display = (
        'pk',
        'name',
        'author',
        favorite_amount,
        tags_line,
    )

    inlines = (
        IngredientInRecipeInline,
    )

    list_filter = ('author', 'name', 'tags', )
    search_fields = ('name', 'author__email', 'tags__name')


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'ingredient',
        'recipe',
        'amount',
    )


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )
    prepopulated_fields = {"slug": ("name",)}


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'recipe',
        'user',
    )


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
    )


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'follow',
        'follower',
    )


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
