from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, generics, status
from genres.serializers import GenresSerializer
from genres.models import GenresModel


# Create your views here.
class GenresView(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = GenresModel.objects.all()
    serializer_class = GenresSerializer

    @swagger_auto_schema(responses={
        status.HTTP_200_OK: serializer_class()
    })
    def get(self, request, *args, **kwargs):
        """Список всех жанров"""
        return self.list(request, *args, **kwargs)
