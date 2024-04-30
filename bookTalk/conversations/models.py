from django.db import models

from authorisation.models import User
from clubs.models import ClubModel


# Create your models here.
class ConversationModel(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=150)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(ClubModel, on_delete=models.CASCADE)


class MessageModel(models.Model):
    id = models.IntegerField(primary_key=True)
    conversation = models.ForeignKey(ConversationModel, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
