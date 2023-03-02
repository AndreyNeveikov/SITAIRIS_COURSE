from rest_framework import serializers

from core.serializers import ImageSerializer
from page.models import Page, Tag
from page.services import PageService
from user.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


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


class PageSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Page
        fields = ('id', 'name', 'uuid', 'description', 'tags',
                  'owner', 'followers', 'image', 'is_private')


class FullPageSerializer(PageSerializer):
    class Meta:
        model = Page
        fields = ('id', 'name', 'uuid', 'description', 'tags', 'owner',
                  'followers', 'image', 'is_private', 'follow_requests',
                  'is_blocked', 'unblock_date')


class PageOwnerSerializer(PageSerializer):
    class Meta:
        model = Page
        fields = ('id', 'name', 'uuid', 'description', 'tags', 'owner',
                  'followers', 'image', 'is_private', 'follow_requests')


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
        if self.instance.unblock_date:
            PageService.unblock_page_task(self.instance)
        message = PageService.get_block_status_message(self.instance)
        return message


class AcceptFollowRequestSerializer(serializers.Serializer):  # noqa
    follow_requests = serializers.IntegerField()

    def validate(self, data):
        user_id = data['follow_requests']
        if not self.instance.follow_requests.filter(id=user_id):
            raise serializers.ValidationError({
                'error': 'User not in the follow requests list.'
            })
        return data

    def update(self, instance, validated_data):
        user_id = validated_data.pop('follow_requests')
        instance.follow_requests.remove(user_id)
        instance.followers.add(user_id)
        message = {'status': {'user': user_id, 'accepted': True}}
        return message


class DeclineFollowRequestSerializer(AcceptFollowRequestSerializer):  # noqa
    def update(self, instance, validated_data):
        user_id = validated_data.pop('follow_requests')
        instance.follow_requests.remove(user_id)
        message = {'status': {'user': user_id, 'decline': True}}
        return message
