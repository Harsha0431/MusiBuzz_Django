from django.db import models
from django.contrib.auth.models import User


class SpotifyToken(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255, default='')
    refresh_token = models.CharField(max_length=255, default='')
