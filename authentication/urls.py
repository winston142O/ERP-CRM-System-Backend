from django.urls import path
from .views import (
    UserRegistrationAPIView,
    UserLoginAPIView,
    ResetPasswordAPIView,
    ResetPasswordConfirmAPIView
)
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView

urlpatterns = [
    path('register/', UserRegistrationAPIView.as_view(), name='user_registration'),
    path('login/', UserLoginAPIView.as_view(), name='user_login'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('reset-password/', ResetPasswordAPIView.as_view(), name='reset_password'),
    path('confirm-reset-password/', ResetPasswordConfirmAPIView.as_view(), name='reset_password_confirm'),
]
