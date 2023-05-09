from rest_framework import serializers

from page.models import Tag
from post.models import Post

class TagSerializerPost(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')

class PostSerializer(serializers.ModelSerializer):
    tags = TagSerializerPost(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'page', 'title', 'content', 'reply_to', 'tags',
                  'created_at', 'updated_at', 'liked_by')


# class PostSerializer(serializers.ModelSerializer):
#     class Meta:
#         image = PageImageSerializer()
#         model = Post
#         fields = ('id', 'page', 'content', 'reply_to',
#                   'created_at', 'updated_at', 'liked_by', 'image')


class PostCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('id', 'page', 'title', 'content', 'reply_to', 'tags')

    def validate_page(self, page):
        user = self.context['request'].user
        if page not in user.pages.all():
            raise serializers.ValidationError({
                'error': "You cannot save a post to someone else's page."
            })
        return page


class PostUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'reply_to', 'tags')
