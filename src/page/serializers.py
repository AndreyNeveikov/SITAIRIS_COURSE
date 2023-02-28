from rest_framework import serializers

from core.serializers import ImageSerializer
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
                  'owner', 'followers', 'image', 'is_private')


class PageCreateSerializer(serializers.ModelSerializer):
    image_file = ImageSerializer(read_only=True)
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Page
        fields = ('id', 'uuid', 'name', 'description', 'image_file',
                  'owner', 'tags', 'image', 'is_private')

    def validate(self, data):
        if 'image_file' in self.initial_data:
            serializer = ImageSerializer(data=self.initial_data)
            serializer.is_valid(raise_exception=True)
            image_url = serializer.save()
            data['image'] = image_url
        return data


class PageUpdateSerializer(PageCreateSerializer):
    def validate(self, data):
        if 'image_file' in self.initial_data:
            serializer = ImageSerializer(data=self.initial_data)
            serializer.is_valid(raise_exception=True)
            image_url = serializer.save(instance=self.instance)
            data['image'] = image_url
        return data


class FullPageSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    owner = UserSerializer(read_only=True)
    followers = UserSerializer(read_only=True, many=True)
    follow_requests = UserSerializer(read_only=True, many=True)

    class Meta:
        model = Page
        fields = ('id', 'name', 'uuid', 'description', 'tags',
                  'owner', 'followers', 'image', 'is_private',
                  'follow_requests', 'is_blocked', 'unblock_date')


class PageOwnerSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    owner = UserSerializer(read_only=True)
    followers = UserSerializer(many=True)

    class Meta:
        model = Page
        fields = ('id', 'name', 'uuid', 'description', 'tags',
                  'owner', 'followers', 'image', 'is_private',
                  'follow_requests', 'is_blocked', 'unblock_date')
        read_only_fields = ('is_blocked', 'unblock_date')


class BlockPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('is_blocked', 'unblock_date')
        extra_kwargs = {
            'is_blocked': {'required': True},
            'unblock_date': {'required': True}
        }

    def save(self, **kwargs):
        super().save(**kwargs)
        message = {'status': {'page': self.instance.id,
                              'blocked': self.instance.is_blocked,
                              'unblock date': self.instance.unblock_date}
                   }
        return message
