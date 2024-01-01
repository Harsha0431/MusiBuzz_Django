from django.contrib import admin
from . import models

admin.site.register(models.UserTrackPlaylist)
admin.site.register(models.UserPlaylists)
admin.site.register(models.UserLikedTracks)
admin.site.register(models.UserInterestedTracks)
