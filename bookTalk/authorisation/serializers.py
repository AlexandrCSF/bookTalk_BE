from rest_framework import serializers
from authorisation.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'is_superuser', 'username', 'first_name', 'last_name', 'date_joined', 'email', 'city']


class UserRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
