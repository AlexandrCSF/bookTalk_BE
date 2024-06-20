from os import environ
import django
from django.forms import model_to_dict
from rest_framework import serializers
from elasticsearch.exceptions import NotFoundError

environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookTalk.settings')
django.setup()
from clubs.models import ClubModel
from search.client import ElasticClient

class ElasticParser:

    def __init__(self):
        self.json_clubs = []
        self.client = ElasticClient()

    def fill_elastic(self):
        self.delete_index()
        self.create_index()
        self.parse()

    def delete_index(self):
        try:
            self.client.indices().delete(index=self.client.index)
        except NotFoundError as ignore:
            pass


    def create_index(self):
        self.client.indices().create(index=self.client.index)

    def parse(self):
        clubs = ClubModel.objects.all()
        club_admins = {}
        for club in ClubModel.objects.all():
            club_admins[club.id] = club.admin.username
        id = 1
        for club in clubs:
            self.json_clubs.append({"index": {"_index": self.client.index, "_id": id}})
            club_dict = model_to_dict(club, fields=[field.name for field in club._meta.fields])
            club_dict['admin'] = club_admins[club.id]
            self.json_clubs.append(club_dict)
            id += 1
        self.client.bulk(self.json_clubs)


ElasticParser().fill_elastic()
