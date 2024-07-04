from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer
)
from django.contrib.auth import login
from rest_framework.permissions import AllowAny
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .helpers.utils import authenticate_uuid_token
from django.core.mail import EmailMultiAlternatives
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
import logging
import os

# Initialize logger
logger = logging.getLogger(__name__)


class UserRegistrationAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request) -> Response:
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request) -> Response:

        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            token_data = serializer.create(serializer.validated_data)
            return Response(token_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordAPIView(APIView):
    """ Generates and sends the required UID and Token required for the user
        to reset their password.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        # Get the user's email from the request
        email = request.data.get('email')

        if not email:
            return Response({'message': 'No email address was provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the email
        form = PasswordResetForm(data={'email': email})

        if form.is_valid():
            for user in form.get_users(email):
                # Token an UID generated to verify user identity
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                mail_subject = 'Password Reset Requested'
                message = render_to_string('password_reset_email.html', {
                    'user': user,
                    'uid': uid,
                    'token': token,
                    'domain': os.getenv('FRONT_END_BASE_URL'),
                })
                email = EmailMultiAlternatives(mail_subject, message, to=[email])
                email.content_subtype = "html"
                email.send()
                logger.info(f'Password reset email sent to {user.email}')

            return Response({"message": "Password reset email has been sent."}, status=200)
        else:
            return Response({"message": "Invalid email address."}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class ResetPasswordConfirmAPIView(APIView):
    """ Allows the user to reset its password after providing the required
        UID and Token generated prior to the request.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        uidb64 = request.GET.get('uid')
        token = request.GET.get('token')

        # Verify that all necessary data is present
        if not all([uidb64, token]):
            return Response({'message': 'Missing required credentials'}, status=status.HTTP_400_BAD_REQUEST)

        auth_result = authenticate_uuid_token(uidb64, token)
        if auth_result is None:
            return Response({"error": "Invalid token."}, status=400)

        user, uid = auth_result

        # Check that the token is valid
        if default_token_generator.check_token(user, token):
            # Get the new password from the request
            new_password = request.data.get('new_password')

            if not new_password:
                return Response({'message': 'No password was provided'}, status=status.HTTP_400_BAD_REQUEST)

            # Set the user's new password
            user.set_password(new_password)
            user.save()

            return Response({"message": "Password has been reset."}, status=200)
        else:
            return Response({"error": "Invalid token."}, status=400)
