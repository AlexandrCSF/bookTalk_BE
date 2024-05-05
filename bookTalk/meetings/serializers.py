from rest_framework import serializers

from meetings.models import MeetingModel


class IWillAttendSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    meeting_id = serializers.IntegerField()


class MeetingCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    date = serializers.DateField()
    time = serializers.TimeField()
    location = serializers.CharField()


class MeetingRequestSerializer(serializers.Serializer):
    meeting_id = serializers.IntegerField()


class MeetingPatchSerializer(serializers.Serializer):
    name = serializers.CharField()
    date = serializers.DateField()
    time = serializers.TimeField()
    location = serializers.CharField()

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingModel
        fields = '__all__'
