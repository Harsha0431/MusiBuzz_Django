import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
import spotipy

from django.contrib.auth.models import User
from .models import UserTrackPlaylist, UserPlaylists, UserLikedTracks, UserInterestedTracks
from spotify_api.models import TrackFeatures


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
    playlist_name = request.data["playlist_name"] or None
    track_id = request.data["track_id"] or None
    if playlist_name is None or track_id is None:
        return JsonResponse({"code": 0, "message": "Invalid playlist or track"})
    try:
        playlist_name_found = UserPlaylists.objects.filter(username=user,playlist_name=playlist_name).exists()
        if not playlist_name_found:
            return JsonResponse({"code": 0, "message": f"Playlist with title `{request.data['playlist_name']}` doesn't "
                                                       f"exist"})
        track_instance, created = TrackFeatures.objects.get_or_create(track_id=track_id)
        UserTrackPlaylist.objects.create(username=user, playlist_name=playlist_name, track_id=track_instance)
        return JsonResponse({"code": 1, "message": "Track added to your playlist"})
    except Exception as e:
        if '"UserTrackPlaylist.playlist_name" must be a "UserPlaylists" instance' in str(e):
            return JsonResponse({"code": 0, "message": f"Playlist with title `{request.data['playlist_name']}` doesn't "
                                                       f"exist"})
        if 'UNIQUE constraint failed' in str(e):
            return JsonResponse({"code": 0, "message": "Track already exists in your playlist"})
        print(f"Exception in adding track to playlist: \n{e}")
        return JsonResponse({"code": -1, "message": 'Failed to add track to your playlist'})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def add_track_to_liked_list(request):
    user = request.user
    track_id = request.data['track_id']
    if track_id is None:
        return JsonResponse({"code": -1, "message": "Invalid track"})
    try:
        is_in_liked_list = UserLikedTracks.objects.filter(username=user, track_id=track_id).exists()
        if is_in_liked_list:
            return JsonResponse({"code": 1, "message": "Track already exists in user liked list"})
        track_instance, created = TrackFeatures.objects.get_or_create(track_id=track_id)
        UserLikedTracks.objects.create(username=user, track_id=track_instance)
        return JsonResponse({"code": 1, "message": "Add to liked list"})
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            return JsonResponse({"code": 0, "message": "This track already exist in your liked list"})
        print(f"Exception in adding track to liked list: \n{e}")
        return JsonResponse({"code": -1, "message": 'Failed to add track to liked list'})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def remove_track_from_liked_list(request):
    user = request.user
    track_id = request.data['track_id']
    if track_id is None:
        return JsonResponse({"code": -1, "message": "Invalid track"})
    try:
        is_in_liked_list = UserLikedTracks.objects.filter(username=user, track_id=track_id).exists()
        if not is_in_liked_list:
            return JsonResponse({"code": 1, "message": "Track unliked"})
        UserLikedTracks.objects.filter(username=user, track_id=track_id).delete()
        return JsonResponse({"code": 1, "message": "Track unliked"})
    except UserLikedTracks.DoesNotExist:
        return JsonResponse({"code": -1, "message": f"Track with track_id {track_id} not found in liked list"})
    except Exception as e:
        print(f"Exception in removing track to liked list: \n{e}")
        return JsonResponse({"code": -1, "message": 'Failed to remove track to liked list'})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def get_liked_tracks_list(request):
    user = request.user
    try:
        data = list(UserLikedTracks.objects.filter(username=user).values("track_id"))
        li = list()
        for track in data:
            li.append(track["track_id"])
        return JsonResponse({"code": 1, "data": li})
    except Exception as e:
        print(f"Exception in getting liked list: \n{e}")
        return JsonResponse({"code": -1, "message": 'Failed to get liked list'})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def get_interested_tracks_list(request):
    user = request.user
    try:
        data = list(UserInterestedTracks.objects.filter(username=user).values("track_id"))
        li = list()
        for track in data:
            li.append(track["track_id"])
        return JsonResponse({"code": 1, "data": li})
    except Exception as e:
        print(f"Exception in getting interested list: \n{e}")
        return JsonResponse({"code": -1, "message": 'Failed to get interested list'})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def add_track_to_interested_list(request):
    user = request.user
    track_list = request.data['track_list']
    if track_list is None:
        return JsonResponse({"code": -1, "message": "Invalid track"})
    try:
        for track in track_list:
            is_exist = UserInterestedTracks.objects.filter(username=user, track_id=track).exists()
            if not is_exist:
                track_instance, created = TrackFeatures.objects.get_or_create(track_id=track)
                # Create UserInterestedTracks instance linking the user and track
                UserInterestedTracks.objects.create(username=user, track_id=track_instance)
        return JsonResponse({"code": 1, "message": "Test Successful"})
    except Exception as e:
        print(f"Exception in adding track to interested list: \n{e}")
        return JsonResponse({"code": -1, "message": 'Failed to add track to interested list'})
