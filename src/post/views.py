from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsAdmin, IsModerator
from post.models import Post
from post.permissions import IsPostOwner
from post.serializers import (PostSerializer, PostCreateSerializer,
                              PostUpdateSerializer)
from post.services import PostService
from user.serializers import UserSerializer


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_action_classes = {
        'update': [IsPostOwner],
        'partial_update': [IsPostOwner],
        'destroy': [IsPostOwner | IsAdmin | IsModerator],
        'list': [IsAuthenticated, IsAdmin | IsModerator],
    }
    serializer_action_classes = {
        'create': PostCreateSerializer,
        'update': PostUpdateSerializer,
        'partial_update': PostUpdateSerializer,
    }

    def get_permissions(self):
        permissions_for_action = self.permission_action_classes.get(
            self.action, [IsAuthenticated]
        )
        return [permission() for permission in permissions_for_action]

    @action(detail=True, methods=['get'])
    def like(self, request, *args, **kwargs):
        post = self.get_object()
        message = PostService.toggle_like(request, post)
        return Response(data=message, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def liked_posts(self, request, *args, **kwargs):
        liked_posts = Post.objects.filter(liked_by=request.user)
        serializer = PostSerializer(instance=liked_posts, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def total_likes(self, request, *args, **kwargs):
        post = self.get_object()
        total_likes = post.liked_by.count()
        return Response(data={'post': post.id, 'total_likes': total_likes},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def like_users_list(self, request, *args, **kwargs):
        post = self.get_object()
        like_users_list = post.liked_by.all()
        serializer = UserSerializer(instance=like_users_list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
