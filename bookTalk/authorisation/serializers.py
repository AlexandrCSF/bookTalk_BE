from rest_framework import serializers
from authorisation.models import User
from clubs.models import CityModel
from genres.serializers import GenresSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'is_superuser', 'username', 'first_name', 'last_name', 'date_joined', 'email', 'city', 'uuid',
                  'refresh_token', 'interests']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['interests'] = GenresSerializer(instance.interests.all(), many=True).data
        return representation


class UserRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()


class UserCreateSerializer(serializers.ModelSerializer):
    interests = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'date_joined', 'email', 'city', 'interests']


class UserPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['is_superuser', 'username', 'first_name', 'last_name', 'date_joined', 'email', 'city']

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class FreeTokenSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(read_only=True)
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)


class UserUUidSerializerRequest(serializers.Serializer):
    uuid = serializers.CharField(required=True)


class TokenRefreshSerializerRequest(serializers.Serializer):
    refresh = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
