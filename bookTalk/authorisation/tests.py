from django.test import TestCase, RequestFactory
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from authorisation.models import User
from authorisation.views import UserView
from clubs.models import CityModel
from genres.models import GenresModel


# Create your tests here.
class TestUser(TestCase):

    def setUp(self):
        CityModel.objects.create(name='test_city', city_fias='test_city')
        GenresModel.objects.create(id='1', name='test_genre')
        User.objects.create(id=1, first_name='Тестовый аккаунт', username='test_user')
        self.factory = RequestFactory()
        self.access_token = RefreshToken.for_user(User.objects.get(username='test_user')).access_token

    def test_card(self):
        request = self.factory.get('auth/user/?user_id=1', HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = UserView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['password'], None)
        self.assertEqual(response.data['first_name'], 'Тестовый аккаунт')

    def test_add_user(self):
        body = {
            "username": "test_user_create",
            "first_name": "test_user_create",
            "password": "test_user_create",
            "last_name": "test_user_create",
            "date_joined": "2024-06-20T16:29:50.611Z",
            "email": "test_user_create@mail.com",
            "city": "test_city",
            "interests": [
                "test_genre"
            ]
        }
        request = self.factory.post('auth/user/?uuid=test_user', data=body, content_type='application/json',
                                    HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = UserView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
