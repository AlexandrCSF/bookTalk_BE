import secrets

from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from authorisation.models import User
from authorisation.serializers import UserRequestSerializer, UserSerializer, UserPatchSerializer, FreeTokenSerializer, \
    FreeTokenSerializerRequest


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
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=FreeTokenSerializerRequest())
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
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user_id': user.id
        }, status=200)
