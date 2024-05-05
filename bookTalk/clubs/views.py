from django.contrib.auth import get_user_model
from django.forms import model_to_dict
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from authorisation.models import User
from authorisation.serializers import UserSerializer, UserRequestSerializer
from clubs.serializers import ClubCardSerializer, ClubCreateSerializer, ClubPatchSerializer, ClubRequestSerializer, \
    SubscribeSerializer
from clubs.models import ClubModel, UserClubModel
from meetings.models import MeetingModel
from meetings.serializers import MeetingSerializer


class ClubCardView(generics.GenericAPIView):
    queryset = ClubModel.objects.all()

    @swagger_auto_schema(query_serializer=ClubRequestSerializer(), responses={
        status.HTTP_200_OK: ClubCardSerializer()
    })
    def get(self, request, *args, **kwargs):
        """
        Карточка Клуба
        """
        club_id = self.request.query_params['club_id']
        club = ClubModel.objects.get(id=club_id)
        serializer = ClubCardSerializer(club)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(query_serializer=ClubRequestSerializer(),
                         responses={200: ClubCardSerializer()})
    def delete(self, request, *args, **kwargs):
        """
        Удаление клуба
        """
        serializer = self.ClubRequestSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        club = ClubModel.objects.get(id=serializer.validated_data['club_id'])
        data = model_to_dict(club)
        club.delete()
        return Response(status=status.HTTP_200_OK, data=data)

    @swagger_auto_schema(request_body=ClubCreateSerializer())
    def put(self, request, *args, **kwargs):
        """
        Добавление клуба
        """
        serializer = ClubCreateSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        new_club = serializer.validated_data
        city = new_club.pop('city_fias')
        new_club['city'] = city
        ClubModel.objects.create(**new_club)
        new_club['city'] = model_to_dict(city)
        return Response(status=status.HTTP_200_OK, data=new_club)

    @swagger_auto_schema(request_body=ClubPatchSerializer(),
                         query_serializer=ClubRequestSerializer(),
                         responses={200: ClubCardSerializer()})
    def patch(self, request, *args, **kwargs):
        """
        Редактирование клуба
        """
        id = request.query_params.get('club_id')
        if not id:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'club_id is required'})

        club = get_object_or_404(ClubModel, id=id)

        serializer = ClubPatchSerializer(club, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = ClubModel.objects.get(id=id)
            return Response(status=status.HTTP_200_OK, data=model_to_dict(response))
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class ClubUsersView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        club_id = self.request.query_params.get('club_id')
        if club_id is None:
            return get_user_model().objects.none()
        return UserClubModel.objects.filter(club_id=club_id).values_list('user_id', flat=True)

    @swagger_auto_schema(query_serializer=ClubRequestSerializer())
    def get(self, request, *args, **kwargs):
        """
        Получить список пользователей для клуба
        """
        queryset = self.get_queryset()
        users = User.objects.filter(id__in=queryset)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MemberView(generics.GenericAPIView):
    serializer_class = ClubCardSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id is None:
            return UserClubModel.objects.none()
        return UserClubModel.objects.filter(user_id=user_id).values_list('club_id', flat=True)

    @swagger_auto_schema(query_serializer=UserRequestSerializer())
    def get(self, request, *args, **kwargs):
        """
        Получить список клубов, в которые вступил пользователь
        """
        queryset = self.get_queryset()
        clubs = ClubModel.objects.filter(id__in=queryset)
        serializer = self.get_serializer(clubs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminView(generics.GenericAPIView):
    serializer_class = ClubCardSerializer

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id is None:
            return ClubModel.objects.none()
        return ClubModel.objects.filter(admin_id=user_id)

    @swagger_auto_schema(query_serializer=UserRequestSerializer())
    def get(self, request, *args, **kwargs):
        """
        Получить список клубов, которыми управляет пользователь
        """
        clubs = self.get_queryset()
        serializer = self.get_serializer(clubs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscribeView(generics.GenericAPIView):
    @swagger_auto_schema(query_serializer=SubscribeSerializer())
    def post(self, request, *args, **kwargs):
        """
        Вступить в клуб
        """
        user = User.objects.get(id=self.request.query_params['user_id'])
        club = ClubModel.objects.get(id=self.request.query_params['club_id'])
        UserClubModel.objects.create(user=user, club=club)
        return Response(data={"user": model_to_dict(user), "club": model_to_dict(club)}, status=200)


class MeetingView(generics.GenericAPIView):
    queryset = MeetingModel.objects.all()

    @swagger_auto_schema(query_serializer=ClubRequestSerializer(), responses={
        status.HTTP_200_OK: MeetingSerializer()
    })
    def get(self, request, *args, **kwargs):
        """
        Список встреч для клуба
        """
        club_id = self.request.query_params['club_id']
        meeting = MeetingModel.objects.filter(club_id=club_id)
        serializer = MeetingSerializer(meeting, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
