from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, generics, serializers, status
from rest_framework.response import Response
from clubs.serializers import ClubCardSerializer
from clubs.models import ClubModel


class ClubCardView(mixins.RetrieveModelMixin, generics.GenericAPIView):
    """
    Карточка Клуба
    """

    serializer_class = ClubCardSerializer
    queryset = ClubModel.objects.all()

    class ClubRequestSerializer(serializers.Serializer):
        club_id = serializers.CharField(required=True)

        class Meta:
            fields = ['club_id']

    @swagger_auto_schema(query_serializer=ClubRequestSerializer(), responses={
        status.HTTP_200_OK: serializer_class()
    })
    def get(self, request, *args, **kwargs):
        serializer = self.ClubRequestSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        club = ClubModel.objects.get(id=serializer.validated_data['club_id'])
        serializer = self.get_serializer(club)
        return Response(serializer.data, status=status.HTTP_200_OK)
