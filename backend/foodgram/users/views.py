from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from .serializers import UserSerializer, MeUserSerializer
from .models import CustomUser
from recipes.models import Subscription
from api.serializers import (
    SubscribeUserSerializer,
    SubscribeSerializer,
)


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination

    @action(
        methods=["POST", "DELETE"],
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=[IsAuthenticated],
        detail=True
    )
    def subscribe(self, request, pk):
        follow = get_object_or_404(CustomUser, id=pk)
        follower = get_object_or_404(CustomUser, id=request.user.id)

        serializer = SubscribeSerializer(
            data={'follow': follow, 'follower': follower}
        )

        if request.method == "POST":
            if Subscription.objects.filter(
                follow=follow,
                follower=follower
            ).exists():
                return Response(
                    f'User -- {follow} -- already followed by user: '
                    f'{follower}', status=status.HTTP_400_BAD_REQUEST
                )
            if follow == follower:
                return Response(
                    'You can not follow yourself!',
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.is_valid(raise_exception=True)
            serializer.save(follow=follow, follower=follower)
            serializer = SubscribeUserSerializer(follow)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not Subscription.objects.filter(
            follow=follow,
            follower=follower
        ).exists():
            return Response(
                f'User -- {follow} -- do not followed by user: '
                f'{follower}. Can not delete',
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription = get_object_or_404(
            Subscription,
            follow=follow,
            follower=follower
        )
        subscription.delete()
        return Response(
            f'User -- {follow} -- removed from follow list of user: '
            f'{follower}', status=status.HTTP_204_NO_CONTENT
        )

    @action(
        methods=["GET"],
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=[IsAuthenticated],
        detail=False
    )
    def subscribe_list(self, request):
        follow = CustomUser.objects.filter(follow_user__follower=request.user)
        paginator = PageNumberPagination()
        paginator.page_size = 6
        result_page = paginator.paginate_queryset(follow, request)
        serializer = SubscribeUserSerializer(
            result_page,
            many=True,
            context={'current_user': request.user}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(
        methods=["GET"],
        url_path='me',
        url_name='me',
        permission_classes=[IsAuthenticated],
        detail=False
    )
    def me(self, request):
        current_user = get_object_or_404(CustomUser, id=request.user.id)
        serializer = MeUserSerializer(current_user)
        return Response(serializer.data)
