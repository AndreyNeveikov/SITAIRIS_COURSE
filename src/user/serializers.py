import jwt
from django.contrib.auth import authenticate
from rest_framework import serializers

from innotter import settings
from user.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):  # noqa
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)

        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        data['user'] = user
        return data

    def create(self, validated_data):
        """
        Creating tokens for user
        """
        access_payload = {
            'token_type': 'access',
            'exp': settings.ACCESS_TOKEN_LIFETIME,
            'user_uuid': str(validated_data['user'].uuid)
        }
        access_token = jwt.encode(payload=access_payload,
                                  key=settings.ACCESS_TOKEN_KEY,
                                  algorithm=settings.JWT_ALGORITHM)

        refresh_payload = {
            'token_type': 'refresh',
            'exp': settings.REFRESH_TOKEN_LIFETIME,
            'user_uuid': str(validated_data['user'].uuid)
        }
        refresh_token = jwt.encode(payload=refresh_payload,
                                   key=settings.REFRESH_TOKEN_KEY,
                                   algorithm=settings.JWT_ALGORITHM)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }


class RefreshTokenSerializer(serializers.Serializer):  # noqa
    refresh_token = serializers.CharField(required=True, write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    @staticmethod
    def check_if_access_token_exist(refresh_token):
        return refresh_token and refresh_token.startswith(settings.AUTH_HEADER_PREFIX)

    def validate(self, data):
        validated_data = super().validate(data)

        refresh_token = validated_data.get('refresh_token', None)

        if not self.check_if_access_token_exist(refresh_token):
            raise serializers.ValidationError(
                'Authorization not found. Please send valid token in headers'
            )

        try:
            payload = jwt.decode(
                jwt=refresh_token.replace(settings.AUTH_HEADER_PREFIX, ''),
                key=settings.REFRESH_TOKEN_KEY,
                algorithms=settings.JWT_ALGORITHM
            )
            if payload.get('token_type') != 'refresh':
                raise serializers.ValidationError(
                    'Token type is not refresh.'
                )
            validated_data['payload'] = payload
        except jwt.ExpiredSignatureError:
            raise serializers.ValidationError(
                'Authentication token has expired.'
            )
        except (jwt.InvalidTokenError, jwt.DecodeError):
            raise serializers.ValidationError(
                'Authorization has failed. Please send valid token.'
            )
        return validated_data

    def create(self, validated_data):
        """
        Creating tokens for user
        """
        access_payload = {
            'token_type': 'access',
            'exp': settings.ACCESS_TOKEN_LIFETIME,
            'user_uuid': str(validated_data['payload']['user_uuid'])
        }
        access_token = jwt.encode(payload=access_payload,
                                  key=settings.ACCESS_TOKEN_KEY,
                                  algorithm=settings.JWT_ALGORITHM)

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
