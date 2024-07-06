from django.urls import path
from .views import (
    UserLoginAPIView,
    ResetPasswordAPIView,
    UserAccountRequestAPIView,
    SignUpApprovalQueueAPIView,
    ResetPasswordConfirmAPIView,
    ApproveSignUpRequestAPIView
)
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView

urlpatterns = [
    path('request-account/', UserAccountRequestAPIView.as_view(), name='user_registration'),
    path('login/', UserLoginAPIView.as_view(), name='user_login'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('reset-password/', ResetPasswordAPIView.as_view(), name='reset_password'),
    path('confirm-reset-password/', ResetPasswordConfirmAPIView.as_view(), name='reset_password_confirm'),
    path('sign-up-approval-queue/', SignUpApprovalQueueAPIView.as_view(), name='signup_approval_queue'),
    path('approve-sign-up-request/<int:approval_request_id>/', ApproveSignUpRequestAPIView.as_view(), name='approve_signup_request'),
]
