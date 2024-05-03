from rest_framework import serializers
from clubs.models import ClubModel, GenresModel, CityModel


class ClubCardSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    city = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    interests = serializers.SlugRelatedField(many=True, read_only=False, slug_field='name',
                                             queryset=GenresModel.objects.all())

    class Meta:
        model = ClubModel
        fields = ('id', 'name', 'description', 'city', 'interests')
        read_only_fields = ('id', 'city')
        many = False


class ClubCardSerializerRequest(serializers.ModelSerializer):
    name = serializers.CharField()
    description = serializers.CharField()
    city_fias = serializers.CharField(max_length=50)
    interests = serializers.PrimaryKeyRelatedField(many=True, queryset=GenresModel.objects.all())

    class Meta:
        model = ClubModel
        fields = "__all__"


class ClubCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    city_fias = serializers.SlugRelatedField(many=False, slug_field='city_fias', queryset=CityModel.objects.all())


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CityModel
        fields = '__all__'


class ClubPatchSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    city_fias = serializers.SlugRelatedField(many=False, slug_field='city_fias', queryset=CityModel.objects.all())

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance