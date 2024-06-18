from django.conf import settings

settings.configure()
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
            self.json_clubs.append(club.items())
        self.client.bulk(self.json_clubs)


ElasticParser().parse()
