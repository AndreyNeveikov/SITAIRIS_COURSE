from rest_framework import serializers

from page.models import Page, Tag
from user.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class PageSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)
    followers = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Page
        fields = ('id', 'name', 'uuid', 'description', 'tags',
                  'owner', 'followers', 'image', 'is_private',
                  'follow_requests', 'unblock_date')
        read_only_fields = ('owner',
                            'followers',
                            'unblock_date')


class PageCreateSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Page
        fields = ('id', 'uuid', 'name', 'description',
                  'owner', 'tags', 'image', 'is_private')


class PageUpdateSerializer(PageCreateSerializer):
    pass