import cloudinary.uploader as uploader
from django.contrib.auth import get_user_model
from django.forms import model_to_dict
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from authorisation.models import User
from authorisation.serializers import UserSerializer, UserRequestSerializer
from clubs.serializers import ClubCardSerializer, ClubCreateSerializer, ClubPatchSerializer, ClubRequestSerializer, \
    ClubSearchSerializer
from clubs.models import ClubModel, UserClubModel
from genres.models import GenresModel
from meetings.models import MeetingModel
from meetings.serializers import MeetingSerializer
from utils.view import BaseView
from search.client import ElasticClient


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

    @swagger_auto_schema(request_body=ClubCreateSerializer(), responses={200: ClubCardSerializer()})
    def put(self, request, *args, **kwargs):
        """
        Добавление клуба
        """
        serializer = ClubCreateSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        new_club = serializer.validated_data
        city = new_club.pop('city_fias')
        interests_list = new_club.pop('interests')
        new_club['city'] = city
        club = ClubModel.objects.create(**new_club)
        interests = [
            GenresModel.objects.get(name=name)
            for name in interests_list
        ]
        club.interests.set(interests)
        self.update_elastic(club)
        return Response(status=status.HTTP_200_OK,
                        data=ClubCardSerializer(club).data)

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
            if 'interests' in request.data:
                interests_list = serializer.validated_data.pop('interests')
                interests = [
                    GenresModel.objects.get(name=name)
                    for name in interests_list
                ]
                club.interests.set(interests)
            serializer.save()
            response = ClubCardSerializer(ClubModel.objects.get(id=id))
            return Response(status=status.HTTP_200_OK, data=response.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @swagger_auto_schema(request_body=ClubSearchSerializer, responses={200: ClubCardSerializer(many=True)})
    def post(self, request):
        """Поиск по клубам"""
        search = request.data['search']
        client = ElasticClient()
        club_ids = client.search(search)
        clubs = ClubModel.objects.filter(id__in=club_ids)
        return Response(ClubCardSerializer(clubs, many=True).data, status=200)

    def update_elastic(self, club):
        client = ElasticClient()
        data = [{"index": {"_index": client.index, "_id": client._client.count(index=client.index)['count'] + 1}}]
        club_dict = model_to_dict(club, fields=[field.name for field in club._meta.fields])
        club_dict['admin'] = club.admin.username
        data.append(club_dict)
        client.bulk(data)


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


class MemberView(generics.GenericAPIView, BaseView):
    serializer_class = ClubCardSerializer

    def get_queryset(self):
        user_id = self.get_user()
        if user_id is None:
            return UserClubModel.objects.none()
        return UserClubModel.objects.filter(user_id=user_id).values_list('club_id', flat=True)

    def get(self, request, *args, **kwargs):
        """
        Получить список клубов, в которые вступил пользователь
        """
        queryset = self.get_queryset()
        clubs = ClubModel.objects.filter(id__in=queryset)
        serializer = self.get_serializer(clubs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecommendsView(generics.GenericAPIView, BaseView):
    serializer_class = ClubCardSerializer

    def get(self, request, *args, **kwargs):
        """
        Получить список клубов, рекомендованных для пользователя
        """
        user_id = self.get_user()
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
            if user.username=='Not_authorised_user':
                clubs = ClubModel.objects.all()[:10]
                serializer = self.get_serializer(clubs, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            administrated_clubs = ClubModel.objects.filter(admin=user).values_list("id", flat=True)
            membership = ClubModel.objects.filter(
                id__in=UserClubModel.objects.filter(user_id=user_id).values_list("club_id")).values_list("id",
                                                                                                         flat=True)
        except User.DoesNotExist:
            return Response({"error": "user not found"}, status=status.HTTP_404_NOT_FOUND)
        interests = user.interests.all()
        if not interests:
            clubs = ClubModel.objects.filter(city=user.city).exclude(id__in=administrated_clubs).exclude(
                id__in=membership)
            serializer = self.get_serializer(clubs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            clubs = ClubModel.objects.filter(interests__in=interests, city=user.city).exclude(
                id__in=administrated_clubs).exclude(
                id__in=membership)
            if not clubs:
                clubs = ClubModel.objects.all().exclude(id__in=administrated_clubs).exclude(
                    id__in=membership)[:10]
            serializer = self.get_serializer(clubs, many=True)
            sorted_clubs = sorted(serializer.data,
                                  key=lambda x: self.calculate_jaccard_index(ClubModel.objects.get(id=x['id']), user),
                                  reverse=True)
            return Response(sorted_clubs, status=status.HTTP_200_OK)

    def calculate_jaccard_index(self, club, user):
        club_interests = set(club.interests.all())
        user_interests = set(user.interests.all())
        intersection = club_interests.intersection(user_interests)
        union = club_interests.union(user_interests)
        return len(intersection) / len(union)


class AdminView(generics.GenericAPIView, BaseView):
    serializer_class = ClubCardSerializer

    def get_queryset(self):
        user_id = self.get_user()
        if user_id is None:
            return ClubModel.objects.none()
        return ClubModel.objects.filter(admin_id=user_id)

    def get(self, request, *args, **kwargs):
        """
        Получить список клубов, которыми управляет пользователь
        """
        clubs = self.get_queryset()
        serializer = self.get_serializer(clubs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscribeView(generics.GenericAPIView, BaseView):

    @swagger_auto_schema(query_serializer=ClubRequestSerializer())
    def post(self, request, *args, **kwargs):
        """
        Вступить в клуб
        """
        user_id = self.get_user()
        user = User.objects.get(id=user_id)
        club = ClubModel.objects.get(id=self.request.query_params['club_id'])
        user_serializer = UserSerializer(user)
        club_serializer = ClubCardSerializer(club)
        UserClubModel.objects.create(user=user, club=club)
        return Response(data={"user": user_serializer.data, "club": club_serializer.data}, status=200)


class UnsubscribeView(generics.GenericAPIView, BaseView):

    @swagger_auto_schema(query_serializer=ClubRequestSerializer())
    def post(self, request, *args, **kwargs):
        """
        Выйти из клуба
        """
        user_id = self.get_user()
        user = User.objects.get(id=user_id)
        club = ClubModel.objects.get(id=self.request.query_params['club_id'])
        UserClubModel.objects.filter(user=user, club=club).delete()
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


class UploadView(APIView):
    parser_classes = (
        MultiPartParser,
        JSONParser,
    )

    @staticmethod
    def post(request):
        file = request.data.get('picture')
        club_id = request.data.get('club_id')
        user_id = request.data.get('user_id')
        if user_id and club_id:
            return Response({"error": "Only one of the following required: club_id or user_id"},
                            status=status.HTTP_400_BAD_REQUEST)
        upload_data = uploader.upload(file)
        img = upload_data['url']
        if club_id:
            club = get_object_or_404(ClubModel, id=club_id)
            if club:
                club.picture = img
                club.save()
                return Response({
                    'status': 'success',
                    'data': upload_data,
                    'url': img,
                    'club': ClubCardSerializer(club).data,
                }, status=201)
            else:
                return Response({"error": "Club not found"},
                                status=status.HTTP_404_NOT_FOUND)
        if user_id:
            user = get_object_or_404(User, id=user_id)
            if user:
                user.picture = img
                user.save()
                return Response({
                    'status': 'success',
                    'data': upload_data,
                    'url': img,
                    'club': UserSerializer(user).data,
                }, status=201)

            else:
                return Response({"error": "User not found"},
                                status=status.HTTP_404_NOT_FOUND)
