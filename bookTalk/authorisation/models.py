import uuid

from django.contrib.auth.models import Group, AbstractUser, Permission
from django.db import models
from clubs.models import GenresModel, CityModel


class User(AbstractUser):
    password = models.CharField(max_length=128,null=True)
    groups = models.ManyToManyField(Group, related_name="groups")
    user_permissions = models.ManyToManyField(Permission, related_name="permissions")
    refresh_token = models.TextField(null=True, blank=True,)
    city = models.ForeignKey(CityModel, on_delete=models.PROTECT, db_column='city_fias', related_name="users",null=True)
    email = models.EmailField(null=True, blank=True)
    interests = models.ManyToManyField(GenresModel, related_name="users")
    uuid = models.CharField(max_length=100,default=uuid.uuid4, unique=True, editable=False)
    is_verified = models.BooleanField(default=False)
