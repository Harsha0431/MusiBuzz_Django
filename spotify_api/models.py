from django.db import models
from django.contrib.auth.models import User

from .helpers import get_track_id_features


class TrackFeatures(models.Model):
    track_id = models.CharField(max_length=255, primary_key=True)
    artist = models.CharField(max_length=255, blank=True, default=None, null=True)
    features = models.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # If track_features is not provided, fetch and set it before saving
        if not self.features:
            features_obj = get_track_id_features(self.track_id)
            artist = features_obj['artist']
            del features_obj['artist']
            self.artist = artist
            self.features = features_obj
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Track: {self.features['track_name']} - {self.artist}"
