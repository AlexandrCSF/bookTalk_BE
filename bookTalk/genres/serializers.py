from rest_framework import serializers
from .models import GenresModel


class GenresSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=64)

    class Meta:
        model = GenresModel
        fields = ('id', 'name')
