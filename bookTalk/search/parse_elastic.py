from os import environ

import django
environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookTalk.settings')
django.setup()

from clubs.models import ClubModel
from clubs.serializers import ClubCardSerializer
from search.client import ElasticClient


class ElasticParser:
    def __init__(self):
        self.json_clubs = []
        self.client = ElasticClient()

    def parse(self):
        clubs = ClubModel.objects.all()
        clubs_serialized = ClubCardSerializer(clubs, many=True).data
        for club in clubs_serialized:
            club_dict = dict(club.items())
            self.json_clubs.append(club_dict)
        self.client.bulk(self.json_clubs)


ElasticParser().parse()
