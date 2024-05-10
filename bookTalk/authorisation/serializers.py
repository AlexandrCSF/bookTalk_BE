from rest_framework import serializers
from authorisation.models import User
from clubs.models import CityModel


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'is_superuser', 'username', 'first_name', 'last_name', 'date_joined', 'email', 'city', 'uuid',
                  'refresh_token']
        extra_kwargs = {
            'is_superuser': {'required': False},
            'username': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
            'date_joined': {'required': False},
            'email': {'required': False},
            'city': {'required': False},
            'refresh_token': {'required': False},
        }


class UserRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'date_joined', 'email', 'city']


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
