from django.contrib.auth.models import Group, AbstractUser, Permission
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from clubs.models import ClubModel, GenresModel, CityModel


class User(AbstractUser):
    id = models.IntegerField(primary_key=True)
    password = models.CharField(max_length=128)
    groups = models.ManyToManyField(Group,related_name="groups")
    user_permissions = models.ManyToManyField(Permission,related_name="permissions")
    refresh_token = models.TextField()
    name = models.CharField(max_length=255, null=False)
    city = models.ForeignKey(CityModel, on_delete=models.PROTECT)
    email = models.EmailField(null=True)
    interests = models.ManyToManyField(GenresModel)
    clubs = models.ManyToManyField(ClubModel)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
