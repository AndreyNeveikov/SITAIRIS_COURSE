from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from core.constants import Roles
from page.models import Page, Tag
from page.permissions import IsPageOwner, PageIsNotPrivateOrFollower
from page.serializers import (PageCreateSerializer, TagSerializer,
                              PageOwnerSerializer, BlockPageSerializer,
                              FullPageSerializer, PageSerializer,
                              PageUpdateSerializer)
from page.services import TagService, PageService
from user.permissions import IsModerator, IsAdmin


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]


class PageViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    queryset = Page.objects.all()
    permission_action_classes = {
        'retrieve': [IsAuthenticated,
                     PageIsNotPrivateOrFollower | IsAdmin | IsModerator],
        'update': [IsAuthenticated, IsPageOwner],
        'partial_update': [IsAuthenticated, IsPageOwner],
        'list': [IsAuthenticated, IsAdmin | IsModerator],
        'block_page': [IsAuthenticated, IsAdmin | IsModerator],
        'allow_current_follow_request': [IsAuthenticated, IsPageOwner],
        'allow_all_follow_requests': [IsAuthenticated, IsPageOwner]
    }
    serializer_action_classes = {
        'create': PageCreateSerializer,
        'update': PageUpdateSerializer,
        'partial_update': PageUpdateSerializer,
        'block_page': BlockPageSerializer,
    }

    def get_queryset(self):
        if self.request.user.role == Roles.USER.value:
            return Page.objects.filter(is_blocked=False)
        return Page.objects.all()

    def get_serializer_class(self):
        if self.action in self.serializer_action_classes:
            return self.serializer_action_classes.get(self.action)

        if self.request.user.role in (Roles.MODERATOR.value,
                                      Roles.ADMIN.value):
            return FullPageSerializer

        if self.request.user == self.get_object().owner:
            return PageOwnerSerializer

        return PageSerializer

    def get_permissions(self):
        permissions = self.permission_action_classes.get(
            self.action, [IsAuthenticated]
        )
        return [permission() for permission in permissions]

    def create(self, request, *args, **kwargs):
        tags_id = TagService.process_tags(request)
        request.data['tags'] = tags_id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if 'tags' in request.data:
            TagService.set_instance_tags(request, instance)

        serializer = self.get_serializer(instance=instance,
                                         data=request.data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def follow(self, request, *args, **kwargs):
        page = self.get_object()
        message = PageService.toggle_follow_status(request, page)
        return Response(data=message, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['post'])
    def block_page(self, request, *args, **kwargs):
        page = self.get_object()
        serializer = self.get_serializer(instance=page, data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        return Response(data=message, status=status.HTTP_202_ACCEPTED)
