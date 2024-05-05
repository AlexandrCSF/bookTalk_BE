from django.db import models

from genres.models import GenresModel


class CityModel(models.Model):
    city_fias = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=40)


class ClubModel(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    city = models.ForeignKey(CityModel, on_delete=models.PROTECT)
    admin = models.ForeignKey('authorisation.User', on_delete=models.PROTECT)
    description = models.TextField()
    interests = models.ManyToManyField(GenresModel)


class UserClubModel(models.Model):
    id = models.AutoField(primary_key=True)
    club = models.ForeignKey(ClubModel, on_delete=models.CASCADE)
    user = models.ForeignKey('authorisation.User', on_delete=models.CASCADE)