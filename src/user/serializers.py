from django.conf import settings
from django.contrib.auth.models import update_last_login
from rest_framework import serializers

from core.exceptions import InvalidTokenError
from innotter.jwt_service import RefreshTokenService, AccessTokenService
from innotter.redis import redis
from page.models import Page
from user.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128,
                                     min_length=8,
                                     write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):  # noqa
    email = serializers.CharField(max_length=255, write_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    access = serializers.CharField(max_length=255, read_only=True)
    refresh = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        password = data.get('password')
        email = data.get('email')

        user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError(
                {'error': 'No user exists with such email.'}
            )

        if not user.check_password(password):
            raise serializers.ValidationError(
                {'error': 'Invalid password.'}
            )

        if not user.is_active or user.is_blocked:
            raise serializers.ValidationError(
                {'error': 'User is not active or blocked.'}
            )

        data['user'] = user
        return data

    def create(self, validated_data):
        """
        Creating tokens for user
        """
        token_service = AccessTokenService(validated_data=validated_data)
        user = validated_data['user']
        validated_data = token_service.generate_jwt_token_dict(user)
        update_last_login(None, user)

        refresh_token = validated_data['refresh']
        redis.set(name=str(user.uuid),
                  value=settings.AUTH_HEADER_PREFIX + refresh_token)

        return validated_data


class RefreshTokenSerializer(serializers.Serializer):  # noqa
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField()

    def validate(self, data):
        token_service = RefreshTokenService(data)
        token_service.is_valid()
        refresh_token = token_service.token
        user = token_service.get_user_from_payload()

        redis_refresh_token = redis.get(str(user.uuid))

        if not redis_refresh_token:
            raise InvalidTokenError()

        redis_refresh_token = redis_refresh_token.decode('utf-8')

        if redis_refresh_token != refresh_token:
            raise InvalidTokenError()

        data['user'] = user
        return data

    def create(self, validated_data):
        """
        Creating tokens for user
        """
        token_service = RefreshTokenService(validated_data)
        user = validated_data['user']
        validated_data = token_service.generate_jwt_token_dict(user)
        refresh_token = validated_data['refresh']
        redis.set(name=str(user.uuid),
                  value=settings.AUTH_HEADER_PREFIX + refresh_token)
        return validated_data


class UserSerializer(serializers.ModelSerializer):
    following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'uuid', 'email', 'username', 'first_name', 'last_name',
                  'image', 'role', 'title', 'following', 'is_blocked')
        read_only_fields = ('role', 'is_blocked')

    @staticmethod
    def get_following(obj):
        following = Page.objects.filter(followers=obj)
        return following.values_list('id', flat=True)
