from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
import spotipy

from django.contrib.auth.models import User
from .models import UserTrackPlaylist, UserPlaylists


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def create_playlist(request):
    playlist_name = request.data['playlist_name'] or None
    user = request.user
    if user is None or playlist_name is None:
        return JsonResponse({"code": -1, "message": 'Please give valid username and playlist name'})

    try:
        user_obj = UserPlaylists.objects.filter(username=user, playlist_name=playlist_name)
        if user_obj.exists():
            return JsonResponse({"code": 0, "message": 'Playlist with given name already exits'})
        new_instance = UserPlaylists.objects.create(username=user, playlist_name=playlist_name)
        new_instance.save()
        return JsonResponse({"code": 1, "message": "Playlist created"})
    except Exception as e:
        print(f"Exception in creating user playlist: {e}")
        return JsonResponse({"code": -1, "message": "Internal server error"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def add_track_to_playlist(request):
    user = request.user
    return JsonResponse({"message": "Came to add track to play list"})
