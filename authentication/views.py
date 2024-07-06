# Dependency imports
import json
import logging
from django.db.models import Q
from django.db import transaction
from rest_framework import status
from django.contrib.auth import login
from django.forms import model_to_dict
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.encoding import force_bytes
from rest_framework.generics import ListAPIView
from .helpers.utils import authenticate_uuid_token
from django.utils.http import urlsafe_base64_encode
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from rest_framework.permissions import AllowAny, IsAuthenticated

# Utility imports
from .serializers import (
    UserAccountRequestSerializer,
    UserLoginSerializer
)
from .models import SignUpApprovalQueue
from .permission_classes import IsAdminUser
from .pagination import ApprovalListPagination
from personnel_management.models import Department, DepartmentTitles
from .tasks import send_password_reset_email, create_user_and_send_activation_email

# Initialize logger
logger = logging.getLogger(__name__)


class UserAccountRequestAPIView(APIView):
    """
    Request an account to the organization's administrators
    """

    permission_classes = [AllowAny]

    def post(self, request) -> Response:
        serializer = UserAccountRequestSerializer(data=request.data)

        if serializer.is_valid():
            sign_up_request = serializer.save()
            if sign_up_request:
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignUpApprovalQueueAPIView(ListAPIView):
    """
    Retrieve sign-up approval requests and their relevant data
    """

    permission_classes = [IsAuthenticated & IsAdminUser]
    pagination_class = ApprovalListPagination

    def get(self, request) -> Response:

        registration_requests = SignUpApprovalQueue.objects.filter(approved=False)

        # Check if a filter was provided
        name = request.GET.get('name')
        if name is not None:
            registration_requests.filter(
                Q(first_name__icontains=name) |
                Q(last_name__icontains=name)
            )

        # Serialize and paginate the results
        paginated_queryset = self.paginate_queryset(registration_requests)
        if paginated_queryset is not None:
            serializer = UserAccountRequestSerializer(paginated_queryset, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserAccountRequestSerializer(registration_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ApproveSignUpRequestAPIView(APIView):
    """
    Approve a sign-up request and trigger account activation
    """

    permission_classes = [IsAuthenticated & IsAdminUser]

    def post(self, request, approval_request_id: int) -> Response:
        if not approval_request_id:
            return Response({"message": "Approval request ID not submitted."}, status=status.HTTP_400_BAD_REQUEST)

        # Load the request's body
        body = json.loads(request.body)

        # Get the role data
        role_data = {
            "department_id": body.get("department_id"),
            "title_id": body.get("title_id"),
        }
        if not all(role_data.values()):
            return Response({"message": "Missing role data."}, status=status.HTTP_400_BAD_REQUEST)

        # Verify that the roles provided are valid
        department = Department.objects.filter(id=role_data.get("department_id")).first()
        title = DepartmentTitles.objects.filter(id=role_data.get("title_id")).first()
        roles = [department, title]
        if not all(roles):
            return Response({"message": "Provided roles are not valid."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Retrieve the approval request
            approval_request = SignUpApprovalQueue.objects.filter(approved=False, id=approval_request_id).first()
            if not approval_request:
                return Response({"message": "Approval Request does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            approval_request_data = model_to_dict(approval_request)
            approval_request.approved = True
            approval_request.save()

            # Create user and send activation email
            create_user_and_send_activation_email.delay(approval_request_data, role_data)

        return Response({"message": "Account approved."}, status=status.HTTP_200_OK)

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
                send_password_reset_email.delay(user, uid, token, email)

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

            # Activate the user if not already activated
            if not user.is_active:
                user.is_active = True

            user.save()

            return Response({"message": "Password has been reset."}, status=200)
        else:
            return Response({"error": "Invalid token."}, status=400)
