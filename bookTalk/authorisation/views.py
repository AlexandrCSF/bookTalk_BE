import secrets
import uuid
from datetime import datetime

from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from authorisation.models import User
from authorisation.serializers import UserRequestSerializer, UserSerializer, UserUUidSerializerRequest, \
    FreeTokenSerializer, TokenRefreshSerializerRequest, UserCreateSerializer, LoginSerializer
from genres.models import GenresModel
from utils.view import BaseView


class AuthorisationView(generics.GenericAPIView, BaseView):
    queryset = User.objects.all()
    serializer_class = FreeTokenSerializer

    @swagger_auto_schema(request_body=LoginSerializer, responses={status.HTTP_200_OK: FreeTokenSerializer()})
    def post(self, request):
        """
        Войти в профиль
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            login = serializer.data.get('login')
            password = serializer.data.get('password')
            user = User.objects.filter(username=login,password=password).first()
            refresh = self.update_token(user)
            if user is not None:
                return Response({
                    'access_token': str(refresh['access_token']),
                    'refresh_token': str(refresh['refresh_token']),
                    'user_id': refresh['user_id']
                }, status=200)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Invalid username or password'})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class UserView(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @swagger_auto_schema(query_serializer=UserRequestSerializer())
    def get(self, request, *args, **kwargs):
        """
        Получение пользователя
        """
        id = self.request.query_params['user_id']
        user = User.objects.get(id=id)
        return Response(UserSerializer(user).data, status=200)

    @swagger_auto_schema(request_body=UserCreateSerializer(),
                         query_serializer=UserUUidSerializerRequest())
    def post(self, request, *args, **kwargs):
        """
        Добавление пользователя
        """
        uuid = self.request.query_params.get('uuid')
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        interests_list = validated_data.pop('interests')
        user = User.objects.filter(uuid=uuid).first()
        if user:
            serializer = UserSerializer(user, data=validated_data, partial=True)
            validated_data['city'] = validated_data['city'].city_fias
            serializer.is_valid(raise_exception=True)
            interests = [
                GenresModel.objects.get(name=name)
                for name in interests_list
            ]
            user.interests.set(interests)
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            user = User.objects.create_user(**validated_data)
            user.uuid = uuid
            interests = [
                GenresModel.objects.get(name=name)
                for name in interests_list
            ]
            user.interests.set(interests)
            user.save()
            return Response(data=UserSerializer(user).data, status=status.HTTP_201_CREATED)


class FreeTokenView(generics.GenericAPIView, BaseView):
    serializer_class = FreeTokenSerializer

    @swagger_auto_schema(request_body=UserUUidSerializerRequest(), responses={200: FreeTokenSerializer()})
    def post(self, request):
        try:
            user, created = User.objects.get_or_create(uuid=request.data['uuid'],
                defaults={'username': secrets.token_hex(16)})
            if created:
                user.save()
        except User.MultipleObjectsReturned:
            user = User.objects.filter(uuid=request.data['uuid'], is_verified=False, is_active=True).first()

        refresh = self.update_token(user)
        return Response({
            'access_token': str(refresh['access_token']),
            'refresh_token': str(refresh['refresh_token']),
            'user_id': refresh['user_id']
        }, status=200)


class RefreshTokenView(generics.GenericAPIView):
    serializer_class = FreeTokenSerializer

    @swagger_auto_schema(request_body=TokenRefreshSerializerRequest(), responses={200: FreeTokenSerializer()})
    def post(self, request):
        serializer = TokenRefreshSerializerRequest(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data['refresh']
        token = RefreshToken(refresh_token)
        access_token = str(token.access_token)

        user_id = token.access_token.get('user_id')
        user = User.objects.filter(id=user_id, is_active=True).first()
        if user.refresh_token != refresh_token:
            raise TokenError("Invalid token")
        token.set_jti()
        token.set_exp()
        token.set_iat()
        refresh_token = str(token)

        if user is None:
            raise TokenError("User not found")
        if user.refresh_token:
            old_token = OutstandingToken.objects.get(token=user.refresh_token)
            BlacklistedToken.objects.create(token=old_token)
            old_token.delete()
            user.refresh_token = refresh_token
        OutstandingToken.objects.create(token=token,
                                        expires_at=datetime.now() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'])
        user.save()

        return Response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user.id
        }, status=status.HTTP_200_OK)
