from django.db import models
from django.contrib.auth.models import User

from spotify_api.helpers import get_track_id_features
from spotify_api.models import TrackFeatures


class UserPlaylists(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Username")
    playlist_name = models.CharField(max_length=255, verbose_name="Playlist Name")

    def __str__(self):
        return f"Username: {self.username} || Playlist: {self.playlist_name}"

    class Meta:
        unique_together = ('username', 'playlist_name')


class UserTrackPlaylist(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    playlist_name = models.CharField(max_length=255, verbose_name="Playlist Name")
    track_id = models.ForeignKey(TrackFeatures, to_field="track_id", on_delete=models.RESTRICT, verbose_name="Track ID",
                                    related_name="user_track_playlist")

    class Meta:
        unique_together = ('username', 'playlist_name', 'track_id')


# Model that store's user liked songs
class UserLikedTracks(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    track_id = models.ForeignKey(TrackFeatures, to_field="track_id", on_delete=models.RESTRICT, verbose_name="Track ID",
                                 related_name="user_liked_tracks")

    class Meta:
        unique_together = ('username', 'track_id')

    def save(self, *args, **kwargs):
        # If add new loved track to interested list
        if not UserInterestedTracks.objects.filter(username=self.username, track_id=self.track_id):
            UserInterestedTracks.objects.create(username=self.username, track_id=self.track_id)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username}-{self.track_id}"


# Model that deals with user interested tracks and there are user by ML model
class UserInterestedTracks(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    # track_id = models.ForeignKey(TrackFeatures, to_field="track_id", on_delete=models.RESTRICT, verbose_name="Track ID")
    track_id = models.ForeignKey(TrackFeatures, to_field="track_id", on_delete=models.RESTRICT, verbose_name="Track ID",
                                 related_name="user_interested_tracks")

    class Meta:
        unique_together = ('username', 'track_id')

    def __str__(self):
        return f"{self.username}-{self.track_id}"
