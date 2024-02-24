import json
import traceback  # For printing traceback in Exception block


from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
import spotipy

from django.contrib.auth.models import User
from .models import UserTrackPlaylist, UserPlaylists, UserLikedTracks, UserInterestedTracks
from spotify_api.models import TrackFeatures
from .helpers import add_tracks_to_interested_list, get_default_recommended_list
from .helpers_bulk import get_bulk_track_features, get_track_images_list

from spotify_api.helpers import get_recommended_tracks_mixed, get_top_tracks_list


# ML models
from .recommendation_model_ml import (get_recommended_tracks_features_ml,
                                      recommend_tracks_offline_collaborative_filtering)


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
        data = list(UserInterestedTracks.objects.filter(username=user).values_list("track_id", flat=True))
        return JsonResponse({"code": 1, "data": data})
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
        add_tracks_to_interested_list(user, track_list)
        return JsonResponse({"code": 1, "message": "Tracks added to interested list successfully"})
    except Exception as e:
        print(f"Exception in adding track to interested list: \n{e}")
        return JsonResponse({"code": -1, "message": 'Failed to add track to interested list'})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def get_recommended_list(request):
    user = request.user
    top_5_artists = mean_features = []
    try:
        track_feature_list = list(TrackFeatures.objects.filter(user_interested_tracks__username=user).values("features"))
        if len(track_feature_list) == 0 or track_feature_list is None:
            recommended_tracks = get_top_tracks_list()
        else:
            top_5_artists, mean_features = get_recommended_tracks_features_ml(tracks=track_feature_list)
            recommended_tracks = get_recommended_tracks_mixed(top_5_artists, mean_features)
        if len(recommended_tracks) < 1:
            track_list = recommend_tracks_offline_collaborative_filtering(user)
            if len(track_list) > 3:
                return JsonResponse({"code": 1, "data": track_list})
            track_list = get_default_recommended_list(top_5_artists, mean_features)
            return JsonResponse({"code": 1, "data": track_list})
        # Upload newly recommended tracks to database model
        get_bulk_track_features(recommended_tracks)
        return JsonResponse({"code": 1, "data": recommended_tracks})
    except Exception as e:
        print(f"Exception in getting recommended list: {traceback.format_exc()}")
        return JsonResponse({"code": -1, "message": "Internal server error"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def get_top_tracks(request):
    user = request.user
    try:
        pass
    except Exception as e:
        print(f"Exception in getting top tracks list: {e}")
        return JsonResponse({"code": -1, "message": "Internal server error"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def get_listed_tracks_full_details(request):
    try:
        req_data = request.data
        track_list = req_data['track_list'] or []
        if len(track_list) > 0:
            data_list = list(TrackFeatures.objects.filter(track_id__in=track_list)
                             .values('track_id', 'artist', 'features__artist_id',
                                     'track_img', 'features__track_name'))
            return JsonResponse({"code": 1, "data": data_list})

        return JsonResponse({"code": 0, message: 'No tracks found'})

    except Exception as e:
        print(f"Exception in getting liked list full details: {e}")
        return JsonResponse({"code": -1, "message": "Internal server error"})
