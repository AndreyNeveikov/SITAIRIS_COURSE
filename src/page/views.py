from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.permissions import IsAdmin, IsModerator, IsAuthAndNotBlocked
from page.models import Page
from page.permissions import IsPageOwner, PageIsNotBlocked
from page.serializers import (PageCreateSerializer, BlockPageSerializer,
                              PageSerializer, PageUpdateSerializer,
                              AcceptFollowRequestSerializer,
                              DeclineFollowRequestSerializer)
from page.services import PageService
from post.models import Post
from post.serializers import PostSerializer


class PageViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    queryset = Page.objects.all()
    permission_action_classes = {
        'retrieve': [IsAuthAndNotBlocked, IsPageOwner, PageIsNotBlocked |
                     IsAdmin | IsModerator],
        'update': [IsAuthAndNotBlocked, PageIsNotBlocked, IsPageOwner],
        'partial_update': [IsAuthAndNotBlocked, PageIsNotBlocked, IsPageOwner],
        'list': [IsAuthAndNotBlocked, IsAdmin | IsModerator],
        'block_page': [IsAuthAndNotBlocked, IsAdmin | IsModerator],
        'follow': [IsAuthAndNotBlocked, PageIsNotBlocked],
        'accept_follow_request': [IsAuthAndNotBlocked, IsPageOwner],
        'decline_follow_request': [IsAuthAndNotBlocked, IsPageOwner],
    }
    serializer_action_classes = {
        'create': PageCreateSerializer,
        'update': PageUpdateSerializer,
        'partial_update': PageUpdateSerializer
    }

    def get_serializer_class(self):
        return self.serializer_action_classes.get(self.action, PageSerializer)

    def get_permissions(self):
        permissions = self.permission_action_classes.get(
            self.action, [IsAuthAndNotBlocked]
        )
        return [permission() for permission in permissions]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def follow(self, request, *args, **kwargs):
        page = self.get_object()
        message = PageService.toggle_follow_status(request, page)
        return Response(data=message, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['post'])
    def block_page(self, request, *args, **kwargs):
        page = self.get_object()
        serializer = BlockPageSerializer(instance=page, data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        return Response(data=message, status=status.HTTP_202_ACCEPTED)

    def follow_request(self, request, *args, **kwargs):
        serializer = kwargs['serializer'](data=request.data,
                                          instance=self.get_object())
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        return Response(data=message, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def accept_follow_request(self, request, *args, **kwargs):
        return self.follow_request(request, *args, **kwargs,
                                   serializer=AcceptFollowRequestSerializer)

    @action(detail=True, methods=['post'])
    def decline_follow_request(self, request, *args, **kwargs):
        return self.follow_request(request, *args, **kwargs,
                                   serializer=DeclineFollowRequestSerializer)

    @action(detail=True, methods=['get'], url_path='posts')
    def get_page_posts(self, request, pk):
        posts = Post.objects.filter(page=pk)
        serializer = PostSerializer(instance=posts, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
