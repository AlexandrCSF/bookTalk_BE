from os import environ
import django
from rest_framework import serializers

environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookTalk.settings')
django.setup()
from clubs.models import ClubModel
from clubs.serializers import ClubCardSerializer
from search.client import ElasticClient


class ElasticSerializer(serializers.ModelSerializer):
    admin_username = serializers.SerializerMethodField()
    interests_name = serializers.SerializerMethodField()
    city_name = serializers.SerializerMethodField()

    class Meta:
        model = ClubModel
        fields = ['id', 'name', 'description', 'admin_username', 'city_name', 'interests_name']

    def get_admin_username(self, obj):
        return obj.admin.username

    def get_city_name(self, obj):
        return obj.city.name

    def get_interests_name(self, obj):
        return [interest.name for interest in obj.interests.all()]


class ElasticParser:

    def __init__(self):
        self.json_clubs = []
        self.client = ElasticClient()

    def fill_elastic(self):
        self.delete_index()
        self.create_index()
        self.parse()

    def delete_index(self):
        self.client.indices().delete(index=self.client.index)

    def create_index(self):
        self.client.indices().create(index=self.client.index)

    def parse(self):
        clubs = ClubModel.objects.all()
        id = 1
        for club in clubs:
            self.json_clubs.append({"index": {"_index": self.client.index, "_id": id}})
            club_dict = ElasticSerializer(club).data
            self.json_clubs.append(club_dict)
            id += 1
        self.client.bulk(self.json_clubs)


ElasticParser().fill_elastic()
