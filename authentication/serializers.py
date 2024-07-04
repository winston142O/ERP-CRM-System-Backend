from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class UserRegistrationSerializer(serializers.ModelSerializer):
    """ This serializer is used to handle registration logic. """

    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def validate(self, attrs):
        """
        Check that all required fields are present in the input data.
        """

        required_fields = [
            'username',
            'email',
            'password',
            'first_name',
            'last_name'
        ]

        # Check if all required fields are present in attrs
        for field in required_fields:
            if field not in attrs:
                raise serializers.ValidationError(f"{field} is required")

        return attrs

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            'first_name',
            'last_name'
        )


class UserLoginSerializer(serializers.Serializer):
    """ This serializer is responsible for handling user login
        logic and JWT generation.
    """

    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if not user:
                raise serializers.ValidationError('Unable to log in with provided credentials.')

        else:
            raise serializers.ValidationError('Must include "username" and "password".')

        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data['user']

        refresh = RefreshToken.for_user(user)

        return {
            'user_id': user.id,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
