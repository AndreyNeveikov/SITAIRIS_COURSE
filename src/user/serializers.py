from django.contrib.auth import authenticate
from rest_framework import serializers

from innotter.middleware import BaseJWT
from user.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    # write_only - не может быть прочитан клиентской стороной
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password']

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

        # USERNAME_FIELD = email
        user = authenticate(username=email, password=password)

        # authenticate returns None if user not found
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        # check if user is active
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )
        auth = BaseJWT(user=user)

        # validate should return dict
        return {'email': user.email,
                'access_token': auth.get_access_token,
                'refresh_token': auth.get_refresh_token}

        # return {'email': user.email,
        #         'access_token': user.get_access_token,
        #         'refresh_token': user.get_refresh_token}
