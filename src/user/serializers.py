from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from core.exceptions import InvalidTokenError, NoTokenError
from innotter import settings
from innotter.jwt_service import (validate_token,
                                  decode_refresh_token,
                                  generate_jwt_token_dict)
from innotter.redis import redis
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
        validated_data = super().validate(data)
        user = self.context['request'].user
        password = validated_data.get('password', None)

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

        update_last_login(None, user)

        return validated_data

    def create(self, validated_data):
        """
        Creating tokens for user
        """
        user = self.context['request'].user
        validated_data = generate_jwt_token_dict(user)
        redis.set(name=str(user.uuid),
                  value=settings.AUTH_HEADER_PREFIX + validated_data['refresh'])

        return validated_data


class RefreshTokenSerializer(serializers.Serializer):  # noqa
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField()

    def validate(self, data):
        validated_data = super().validate(data)
        refresh_token = validated_data.get('refresh', None)

        if not validate_token(refresh_token):
            raise NoTokenError()

        payload = decode_refresh_token(refresh_token)
        uuid = payload['user_uuid']
        user = get_object_or_404(User, uuid=uuid)

        redis_refresh_token = redis.get(uuid)

        if not redis_refresh_token:
            raise InvalidTokenError()

        redis_refresh_token = redis_refresh_token.decode('utf-8')

        if redis_refresh_token != refresh_token:
            raise InvalidTokenError()

        validated_data['user'] = user
        return validated_data

    def create(self, validated_data):
        """
        Creating tokens for user
        """
        user = validated_data['user']
        validated_data = generate_jwt_token_dict(user)
        redis.set(name=str(user.uuid),
                  value=settings.AUTH_HEADER_PREFIX + validated_data['refresh'])
        return validated_data

        refresh_payload = {
            'token_type': 'refresh',
            'exp': settings.REFRESH_TOKEN_LIFETIME,
            'user_uuid': str(validated_data['payload']['user_uuid'])
        }
        refresh_token = jwt.encode(payload=refresh_payload,
                                   key=settings.REFRESH_TOKEN_KEY,
                                   algorithm=settings.JWT_ALGORITHM)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
