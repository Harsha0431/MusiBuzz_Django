from turtle import onkey

from django.db import models
from django.contrib.auth.models import User


class UserTrackPlaylist(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    playlist_name = models.CharField(max_length=255)
    track_id = models.CharField(max_length=255)

    class Meta:
        unique_together = ('username', 'playlist_name', 'track_id')
