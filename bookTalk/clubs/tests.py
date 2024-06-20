from django.test import TestCase, RequestFactory
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from authorisation.models import User
from clubs.views import ClubCardView
from clubs.models import CityModel, ClubModel
from genres.models import GenresModel


# Create your tests here.
class TestClubs(TestCase):

    def setUp(self):
        CityModel.objects.create(name='test_city', city_fias='test_city')
        GenresModel.objects.create(id='1', name='test_genre')
        User.objects.create(id=1, first_name='Тестовый аккаунт', username='test_user')
        ClubModel.objects.create(id=1, name='test_club', city_id='test_city', admin_id=1)
        self.factory = RequestFactory()
        self.access_token = RefreshToken.for_user(User.objects.get(username='test_user')).access_token

    def test_card(self):
        request = self.factory.get('clubs/club/?club_id=1', HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = ClubCardView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], 1)
        self.assertEqual(response.data['city'], 'test_city')
        self.assertEqual(response.data['name'], 'test_club')

    def test_add_club(self):
        body = {
            "name": "test_club",
            "description": "test_club",
            "admin_id": 1,
            "city_fias": "test_city",
            "interests": [
                "test_genre"
            ]
        }
        request = self.factory.put('clubs/club/', data=body, content_type='application/json',
                                   HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
        response = ClubCardView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
