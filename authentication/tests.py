from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

class AuthenticationTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.login_url = reverse('user_login')

    def test_user_login_valid_credentials(self):
        # Test user login with valid credentials

        data = {'username': 'testuser', 'password': 'testpassword'}

        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        # Additional JWT assertions
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)

    def test_user_login_invalid_credentials(self):
        # Test user login with invalid credentials

        data = {'username': 'testuser', 'password': 'wrongpassword'}

        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)

    def test_user_login_missing_credentials(self):
        # Test user login with missing credentials

        data = {}

        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)

    def test_jwt_tokens_validity(self):
        # Test validity of JWT tokens after login

        data = {'username': 'testuser', 'password': 'testpassword'}

        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        access_token = response.data['access']
        refresh_token = response.data['refresh']

        # Verify access token validity
        token_response = self.client.post(reverse('token_verify'), {'token': access_token}, format='json')
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)

        # Verify new access token (refreshed) validity
        refresh_response = self.client.post(reverse('token_refresh'), {'refresh': refresh_token}, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
