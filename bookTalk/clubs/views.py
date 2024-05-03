from django.forms import model_to_dict
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, serializers, status
from rest_framework.response import Response
from clubs.serializers import ClubCardSerializer, ClubCardSerializerRequest, ClubCreateSerializer, CitySerializer
from clubs.models import ClubModel, CityModel


class ClubCardView(generics.GenericAPIView):
    """
    Карточка Клуба
    """

    queryset = ClubModel.objects.all()

    class ClubRequestSerializer(serializers.Serializer):
        club_id = serializers.CharField(required=True)

        class Meta:
            fields = ['club_id']

    @swagger_auto_schema(query_serializer=ClubRequestSerializer(), responses={
        status.HTTP_200_OK: ClubCardSerializer()
    })
    def get(self, request, *args, **kwargs):
        serializer = self.ClubRequestSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        club = ClubModel.objects.get(id=serializer.validated_data['club_id'])
        serializer = ClubCardSerializer(club)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(query_serializer=ClubRequestSerializer(),
                         responses={200: ClubCardSerializer()})
    def delete(self, request, *args, **kwargs):
        serializer = self.ClubRequestSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        club = ClubModel.objects.get(id=serializer.validated_data['club_id'])
        data = model_to_dict(club)
        club.delete()
        return Response(status=status.HTTP_200_OK, data=data)

    @swagger_auto_schema(request_body=ClubCreateSerializer())
    def post(self, request, *args, **kwargs):
        serializer = ClubCreateSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        new_club = serializer.validated_data
        city = new_club.pop('city_fias')
        new_club['city'] = city
        ClubModel.objects.create(**new_club)
        new_club['city'] = model_to_dict(city)
        return Response(status=status.HTTP_200_OK, data=new_club)
