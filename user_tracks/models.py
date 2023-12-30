from django.db import models
from django.contrib.auth.models import User


class UserPlaylists(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Username")
    playlist_name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('username', 'playlist_name')


class UserTrackPlaylist(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    playlist_name = models.ForeignKey(UserPlaylists, on_delete=models.CASCADE,
                                      verbose_name="Playlist Name", default="playlist")
    track_id = models.CharField(max_length=255)
    track_features = models.JSONField(blank=True, null=True)

    class Meta:
        unique_together = ('username', 'playlist_name', 'track_id')