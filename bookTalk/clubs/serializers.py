from rest_framework import serializers

from authorisation.models import User
from authorisation.serializers import UserSerializer
from clubs.models import ClubModel, GenresModel, CityModel
from genres.serializers import GenresSerializer
from meetings.serializers import MeetingSerializer


class ClubRequestSerializer(serializers.Serializer):
    club_id = serializers.CharField(required=True)

    class Meta:
        fields = ['club_id']


class ClubCardSerializer(serializers.ModelSerializer):
    meetings = MeetingSerializer(many=True, read_only=True)

    class Meta:
        model = ClubModel
        fields = ('id', 'name', 'description', 'admin', 'city', 'interests', 'meetings', 'picture')
        read_only_fields = ('id', 'city')
        many = False

    def calculate_jaccard_index(self, club, user):
        club_interests = set(club.interests.all())
        user_interests = set(user.interests.all())
        intersection = club_interests.intersection(user_interests)
        union = club_interests.union(user_interests)
        return len(intersection) / len(union)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['interests'] = GenresSerializer(instance.interests.all(), many=True).data
        representation['meetings'] = MeetingSerializer(instance.meetings.all(), many=True).data
        representation['admin'] = UserSerializer(instance.admin).data
        return representation


class ClubCardSerializerRequest(serializers.ModelSerializer):
    name = serializers.CharField()
    description = serializers.CharField()
    city_fias = serializers.CharField(max_length=50)
    interests = serializers.PrimaryKeyRelatedField(many=True, queryset=GenresModel.objects.all())

    class Meta:
        model = ClubModel
        fields = "__all__"


class ClubCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    admin_id = serializers.IntegerField()
    city_fias = serializers.SlugRelatedField(many=False, slug_field='city_fias', queryset=CityModel.objects.all())
    interests = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
        required=False
    )


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CityModel
        fields = '__all__'


class ClubPatchSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    city_fias = serializers.SlugRelatedField(many=False, slug_field='city_fias', queryset=CityModel.objects.all())
    admin = serializers.SlugRelatedField(many=False, slug_field='id', queryset=User.objects.all())
    interests = serializers.ListField(child=serializers.CharField())

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ClubSearchSerializer(serializers.Serializer):
    search = serializers.CharField(max_length=50)
