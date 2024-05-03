from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response

from conversations.serializers import ConversationSerializer, MessageSerializer, ConversationRequestSerializer, \
    MessageListRequestSerializer, MessageDestroyRequestSerializer
from conversations.models import ConversationModel, MessageModel
from rest_framework import generics, status
from clubs.models import ClubModel


# Create your views here.

class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer

    @swagger_auto_schema(query_serializer=ConversationRequestSerializer(),
                         responses={200: ConversationSerializer(many=True)})
    def get(self, request, *args, **kwargs):
        """Получение обсуждений для клуба"""
        serializer = ConversationRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        club_id = serializer.validated_data['club_id']
        club = ClubModel.objects.get(id=club_id)
        conversations = ConversationModel.objects.filter(club=club)
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """Создание обсуждения клуба"""
        return super().post(request, *args, **kwargs)


class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    queryset = MessageModel.objects.all()

    @swagger_auto_schema(query_serializer=MessageListRequestSerializer(),
                         responses={200: MessageSerializer(many=True)})
    def get(self, request, *args, **kwargs):
        """Получение сообщений обсуждения"""
        serializer = MessageListRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        conversation_id = serializer.validated_data['conversation_id']
        conversation = ConversationModel.objects.get(id=conversation_id)
        messages = MessageModel.objects.filter(conversation=conversation)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """Создание сообщения обсуждения"""
        return super().post(request, *args, **kwargs)


class MessageDestroyView(generics.DestroyAPIView):
    queryset = MessageModel.objects.all()

    def delete(self, request, *args, **kwargs):
        """Удаление сообщения"""
        return super().destroy(request, *args, **kwargs)


class ConversationDestroyView(generics.DestroyAPIView):
    queryset = ConversationModel.objects.all()

    def delete(self, request, *args, **kwargs):
        """Удаление сообщения"""
        return super().destroy(request, *args, **kwargs)