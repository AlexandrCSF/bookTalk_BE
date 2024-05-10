import secrets
from datetime import datetime

from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from authorisation.models import User
from authorisation.serializers import UserRequestSerializer, UserSerializer, UserPatchSerializer, \
    FreeTokenSerializerRequest, FreeTokenSerializer, TokenRefreshSerializerRequest


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

    @swagger_auto_schema(request_body=UserSerializer())
    def post(self, request, *args, **kwargs):
        """
        Добавление пользователя
        """
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = User.objects.create_user(**validated_data)
        user.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(request_body=UserPatchSerializer(),
                         query_serializer=UserRequestSerializer())
    def patch(self, request, *args, **kwargs):
        """
        Редактирование пользователя
        """
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserPatchSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FreeTokenView(generics.GenericAPIView):
    serializer_class = FreeTokenSerializer

    @swagger_auto_schema(request_body=FreeTokenSerializerRequest(), responses={200: FreeTokenSerializer()})
    def post(self, request):
        try:
            user, created = User.objects.get_or_create(
                uuid=request.data['uuid'], is_verified=False, is_active=True,
                defaults={'username': secrets.token_hex(16)})
            if created:
                user.save()
        except User.MultipleObjectsReturned:
            user = User.objects.filter(uuid=request.data['uuid'], is_verified=False, is_active=True).first()

        refresh = RefreshToken.for_user(user)
        if user.refresh_token:
            old_token = OutstandingToken.objects.filter(token=user.refresh_token)
            if old_token:
                BlacklistedToken.objects.create(token=old_token.first())
                old_token.first().delete()
            if not OutstandingToken.objects.filter(token=refresh):
                OutstandingToken.objects.create(token=refresh, expires_at=datetime.now() + settings.SIMPLE_JWT[
                    'ACCESS_TOKEN_LIFETIME'])
        user.refresh_token = refresh
        user.save()
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user_id': user.id
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
