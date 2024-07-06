from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import SignUpApprovalQueue
from .contants import forbidden_usernames


class UserAccountRequestSerializer(serializers.ModelSerializer):
    """ This serializer is used to handle registration logic. """

    def create(self, validated_data):
        account_request = SignUpApprovalQueue.objects.create(**validated_data)
        return account_request

    def validate(self, attrs):
        """
        Check that all required fields are present in the input data.
        """

        required_fields = [
            'username',
            'email',
            'first_name',
            'last_name'
        ]

        # Check if all required fields are present in attrs
        for field in required_fields:
            if field not in attrs:
                raise serializers.ValidationError(f"{field} is required")

            elif field == 'username':
                username = attrs[field]

                if username in forbidden_usernames:
                    raise serializers.ValidationError(f"Username '{username}' is forbidden")

                # Validate existence
                user_obj = User.objects.filter(username=username).first()
                if user_obj:
                    raise serializers.ValidationError("User already exists")

            elif field == 'email':
                email = attrs[field]

                # Validate existence
                user_obj = User.objects.filter(email=email).first()
                if user_obj:
                    raise serializers.ValidationError("User already exists")

        return attrs

    class Meta:
        model = SignUpApprovalQueue
        fields = (
            'id',
            'requested_date',
            'username',
            'email',
            'first_name',
            'last_name',
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
