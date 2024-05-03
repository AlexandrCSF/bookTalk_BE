from rest_framework import serializers
from conversations.models import ConversationModel, MessageModel


class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationModel
        fields = ['id', 'title', 'description', 'created_by', 'club']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageModel
        fields = ['id', 'conversation', 'author', 'text']


class ConversationRequestSerializer(serializers.Serializer):
    club_id = serializers.IntegerField()


class MessageListRequestSerializer(serializers.Serializer):
    conversation_id = serializers.IntegerField()


class MessageDestroyRequestSerializer(serializers.Serializer):
    message_id = serializers.IntegerField()
