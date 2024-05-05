from django.forms import model_to_dict
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from authorisation.models import User
from authorisation.serializers import UserRequestSerializer
from clubs.models import UserClubModel, ClubModel
from clubs.serializers import ClubRequestSerializer
from meetings.models import MeetingModel, UserMeetingModel
from meetings.serializers import MeetingSerializer, MeetingRequestSerializer, MeetingCreateSerializer, \
    MeetingPatchSerializer, IWillAttendSerializer


class MeetingView(generics.GenericAPIView):
    queryset = MeetingModel.objects.all()

    @swagger_auto_schema(query_serializer=ClubRequestSerializer(), responses={
        status.HTTP_200_OK: MeetingSerializer()
    })
    def get(self, request, *args, **kwargs):
        """
        Списко встреч для клуба
        """
        club_id = self.request.query_params['club_id']
        meeting = MeetingModel.objects.filter(club_id=club_id)
        serializer = MeetingSerializer(meeting, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(query_serializer=MeetingRequestSerializer(),
                         responses={200: MeetingSerializer()})
    def delete(self, request, *args, **kwargs):
        """
        Удаление встречи
        """
        serializer = MeetingRequestSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        meeting = MeetingModel.objects.get(id=serializer.validated_data['meeting_id'])
        data = model_to_dict(meeting)
        meeting.delete()
        return Response(status=status.HTTP_200_OK, data=data)

    @swagger_auto_schema(request_body=MeetingCreateSerializer(),
                         query_serializer=ClubRequestSerializer())
    def put(self, request, *args, **kwargs):
        """
        Добавление встречи
        """
        serializer = MeetingCreateSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        new_meeting = serializer.validated_data
        club = ClubModel.objects.get(id=request.query_params['club_id'])
        new_meeting['club'] = club
        MeetingModel.objects.create(**new_meeting)
        new_meeting['club'] = model_to_dict(club)
        return Response(status=status.HTTP_200_OK, data=new_meeting)

    @swagger_auto_schema(request_body=MeetingPatchSerializer(),
                         query_serializer=MeetingRequestSerializer(),
                         responses={200: MeetingSerializer()})
    def patch(self, request, *args, **kwargs):
        id = request.query_params.get('meeting_id')
        if not id:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'meeting_id is required'})

        meeting = get_object_or_404(MeetingModel, id=id)

        serializer = MeetingPatchSerializer(meeting, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response = MeetingModel.objects.get(id=id)
            return Response(status=status.HTTP_200_OK, data=model_to_dict(response))
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


class AttendanceView(generics.GenericAPIView):
    @swagger_auto_schema(query_serializer=UserRequestSerializer())
    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=self.request.query_params['user_id'])
        meetings = MeetingModel.objects.filter(id__in=UserMeetingModel.objects.filter(user=user).values_list("meeting",flat=True))
        serializer = MeetingSerializer(meetings,many=True)
        return Response(serializer.data,status=200)

    @swagger_auto_schema(query_serializer=IWillAttendSerializer())
    def post(self, request, *args, **kwargs):
        user = User.objects.get(id=self.request.query_params['user_id'])
        meeting = MeetingModel.objects.get(id=self.request.query_params['meeting_id'])
        club = meeting.club
        subscribed = get_object_or_404(UserClubModel, user=user, club=club)
        if subscribed:
            UserMeetingModel.objects.create(user=user, meeting=meeting)
            return Response(data={"user": model_to_dict(user), "meeting": model_to_dict(meeting)}, status=200)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": "User is not subscribed to club"})