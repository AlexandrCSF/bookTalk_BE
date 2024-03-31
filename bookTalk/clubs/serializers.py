from rest_framework import serializers
from .models import ClubModel, GenresModel


class ClubCardSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    city = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    interests = serializers.SlugRelatedField(many=True, read_only=False, slug_field='name', queryset=GenresModel.objects.all())

    class Meta:
        model = ClubModel
        fields = ('id', 'name', 'description', 'city', 'interests')
        read_only_fields = ('id', 'city')
        many = False
