import secrets
from django.test import TestCase, RequestFactory
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status


from authorisation.models import User
from authorisation.views import UserView


# Create your tests here.
class TestUser(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.test_user = User.objects.create(first_name='Тестовый аккаунт', username=secrets.token_hex(16))
        self.access_token = RefreshToken.for_user(self.test_user).access_token

    def test_card(self):
        reqest = self.factory.get('auth/user/?user_id=1', HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = UserView.as_view()(reqest)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['password'], None)
        self.assertEqual(response.data['first_name'], 'Тестовый аккаунт')