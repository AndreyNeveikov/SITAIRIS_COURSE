from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.constants import Roles
from page.models import Page
from page.permissions import (IsPageOwner, PageIsNotBlocked,
                              PageIsNotPrivateOrFollower)
from page.serializers import (PageCreateSerializer, PageOwnerSerializer,
                              BlockPageSerializer, FullPageSerializer,
                              PageSerializer, PageUpdateSerializer,
                              AcceptFollowRequestSerializer,
                              DeclineFollowRequestSerializer)
from page.services import TagService, PageService
from user.permissions import IsModerator, IsAdmin


class PageViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    queryset = Page.objects.all()
    permission_action_classes = {
        'retrieve': [IsAuthenticated, PageIsNotBlocked,
                     PageIsNotPrivateOrFollower | IsAdmin | IsModerator],
        'update': [IsAuthenticated, PageIsNotBlocked, IsPageOwner],
        'partial_update': [IsAuthenticated, PageIsNotBlocked, IsPageOwner],
        'list': [IsAuthenticated, IsAdmin | IsModerator],
        'block_page': [IsAuthenticated, IsAdmin | IsModerator],
        'follow': [IsAuthenticated, PageIsNotBlocked],
        'accept_follow_request': [IsAuthenticated, IsPageOwner],
        'decline_follow_request': [IsAuthenticated, IsPageOwner],
    }

    def get_serializer_class(self):
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
        serializer = PageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if 'tags' in request.data:
            TagService.set_instance_tags(request, instance)

        serializer = PageUpdateSerializer(instance=instance,
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
