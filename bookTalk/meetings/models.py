from django.db import models

from clubs.models import ClubModel


# Create your models here.
class MeetingModel(models.Model):
    id = models.IntegerField(primary_key=True)
    club = models.ForeignKey(ClubModel, on_delete=models.CASCADE, related_name='meetings')
    name = models.CharField(max_length=30, null=False)
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=150)


class UserMeetingModel(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('authorisation.User', on_delete=models.CASCADE)
    meeting = models.ForeignKey(MeetingModel, on_delete=models.CASCADE)
