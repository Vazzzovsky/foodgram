from rest_framework import serializers

from recipes.models import Subscription

from .models import CustomUser




class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        current_recipe_author = obj
        is_subscribed = Subscription.objects.filter(
            follow=current_recipe_author,
            follower=current_user
        ).exists()
        return is_subscribed


class MeUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        return False
