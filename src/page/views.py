from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from core.serializers import ImageSerializer
from page.models import Page, Tag
from page.permissions import IsPageOwner, PageIsNotPrivateOrFollower
from page.serializers import PageSerializer, PageCreateSerializer, TagSerializer, PageUpdateSerializer
from page.services import TagService
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
        'list': PageSerializer,
    }

    # def get_queryset(self):
    #     if self.request.user.role == 'user':
    #         self.queryset.filter()
    #     ...

    def get_serializer_class(self):
        return self.serializer_action_classes.get(self.action, PageSerializer)

    def get_permissions(self):
        permissions = self.permission_action_classes.get(
            self.action, [IsAuthenticated]
        )
        return [permission() for permission in permissions]

    def create(self, request, *args, **kwargs):
        tags_id = TagService.process_tags(request)
        image_url = None
        if 'image' in request.data:
            image_serializer = ImageSerializer(data=request.data)
            image_serializer.is_valid(raise_exception=True)
            image_url = image_serializer.save()

        data = {**request.data, 'tags': tags_id, 'image': image_url}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        image_url = instance.image
        if 'image' in request.data:
            image_serializer = ImageSerializer(data=request.data)
            image_serializer.is_valid(raise_exception=True)
            image_url = image_serializer.save(instance=instance)

        if 'tags' in request.data:
            TagService.set_instance_tags(request, instance)

        data = {**request.data, 'image': image_url}
        serializer = self.get_serializer(instance=instance,
                                         data=data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
