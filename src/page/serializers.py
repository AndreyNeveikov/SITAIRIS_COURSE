from rest_framework import serializers

from core.serializers import ImageInternalValueMixin
from page.models import Page, Tag
from page.services import PageService, TagService
from user.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class PageCreateSerializer(ImageInternalValueMixin,
                           serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ('id', 'uuid', 'name', 'description',
                  'owner', 'tags', 'image', 'is_private')
        read_only_fields = ('owner',)

    def to_internal_value(self, data):
        tags_id = TagService.process_tags(data)
        if tags_id:
            data['tags'] = tags_id
        return super().to_internal_value(data)


class PageUpdateSerializer(PageCreateSerializer):
    def to_internal_value(self, data):
        if 'tags' in data:
            self.instance.tags.clear()
        return super().to_internal_value(data)


class PageSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Page
        fields = ('id', 'name', 'uuid', 'description', 'tags', 'owner',
                  'followers', 'image', 'is_private', 'follow_requests',
                  'is_blocked', 'unblock_date')

    def to_representation(self, instance):
        user = self.context['request'].user
        ret = super().to_representation(instance)
        if user.is_staff or instance.owner == user:
            return ret
        elif user in instance.followers.all() or not instance.is_private:
            for key in ['follow_requests', 'is_blocked', 'unblock_date']:
                ret.pop(key)
            return ret
        else:
            ret = {'id': instance.id, 'is_private': instance.is_private}
            return ret


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
