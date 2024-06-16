import secrets
import uuid
from datetime import datetime

from django.conf import settings
from django.forms import model_to_dict
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken
from authorisation.models import User
from authorisation.serializers import UserRequestSerializer, UserSerializer, UserUUidSerializerRequest, \
    FreeTokenSerializer, TokenRefreshSerializerRequest, UserCreateSerializer, LoginSerializer, UserPatchSerializer
from genres.models import GenresModel
from utils.view import BaseView
from django.contrib.auth import authenticate

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
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = authenticate(email=email, password=password).first()
            if user is not None:
                refresh = self.update_token(user)
                return Response({
                    'access_token': str(refresh['access_token']),
                    'refresh_token': str(refresh['refresh_token']),
                    'user_id': refresh['user_id']
                }, status=200)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Invalid email or password'})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class UserView(generics.GenericAPIView, BaseView):
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
        Добавление пользователя(Регистрация)
        """
        uuid = request.query_params.get('uuid')
        if 'interests' in request.data:
            interests_list = request.data['interests']
            interests = GenresModel.objects.filter(name__in=interests_list).values_list('id', flat=True)
            request.data['interests'] = interests

        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        interests_list = validated_data.pop('interests')

        user = User.objects.filter(uuid=uuid).first()
        if user:
            return Response(data={"text": "Пользователь с таким uuid уже существует"},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            user = User.objects.create_user(**validated_data)
            user.uuid = uuid
            user.interests.set(interests_list)
            user.refresh_token = self.update_token(user)['refresh_token']
            user.is_verified = True
            user.is_active = True
            user.password = request.data['password']
            user.save()
            return Response(data=UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=UserPatchSerializer(),
                         query_serializer=UserRequestSerializer(),
                         responses={200: UserSerializer()})
    def patch(self, request, *args, **kwargs):
        """
        Редактирование клуба
        """
        id = request.query_params.get('user_id')
        if not id:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'user_id is required'})

        user = get_object_or_404(User, id=id)

        serializer = UserPatchSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = User.objects.get(id=id)
            return Response(status=status.HTTP_200_OK, data=model_to_dict(response))
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class FreeTokenView(generics.GenericAPIView, BaseView):
    serializer_class = FreeTokenSerializer
    authentication_classes = []

    @swagger_auto_schema(request_body=UserUUidSerializerRequest(), responses={200: FreeTokenSerializer()})
    def post(self, request):
        refresh = self.update_token(User.objects.get(username='Not_authorised_user'))
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
