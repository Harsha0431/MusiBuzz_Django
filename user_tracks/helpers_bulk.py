from django.http import JsonResponse
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

from spotify_api.credentials import client_ID, client_SECRET, scope, redirect_URI
from spotify_api.models import TrackFeatures

from django.db import transaction
from django.db.models import Q

import pandas as pd
import math
import traceback

from .recommendation_model_ml import recommend_tracks_offline, recommend_tracks_offline_collaborative_filtering


def spotify_callback():
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_ID, client_secret=client_SECRET))
    access_token = sp.auth_manager.get_access_token(as_dict=False)
    return sp


def get_id_from_track_id(track_id):
    track_id_only = track_id.split(':')[2]
    return track_id_only


def get_track_id_popularity_name_uri_artist_name(track_info):
    try:
        artist_obj = track_info['artists'][0]
        track_obj = track_info
        track_id = track_obj['id']
        track_name = track_obj['name']
        track_uri = track_obj['uri']
        popularity = track_obj['popularity']
        artist_name = artist_obj['name']
        artist_id = artist_obj['id']
        json_obj = {"track_id": track_id, "track_name": track_name, "track_uri": track_uri,
                    "popularity": popularity, "artist_name": artist_name, "artist_id": artist_id}
        return json_obj

    except Exception as e:
        print(f"Exception in getting other details of single track:  {e}")
        return None


def get_bulk_track_id_popularity_name_uri_artist_name(track_ids_list):
    try:
        sp = spotify_callback()
        other_features = sp.tracks(track_ids_list)
        return other_features
        pass
    except Exception as e:
        print(f"Exception in getting other details of tracks in bulk:  {e}")
        return None
    pass


def get_track_id_features(track_features, track_popularity_artist):
    try:
        artist = track_popularity_artist["artist_name"]
        artist_id = track_popularity_artist['artist_id']
        popularity = track_popularity_artist["popularity"]
        track_name = track_popularity_artist['track_name']
        danceability = track_features["danceability"]
        energy = track_features["energy"]
        loudness = track_features["loudness"]
        speechiness = track_features["speechiness"]
        acousticness = track_features["acousticness"]
        instrumentalness = track_features["instrumentalness"]
        valence = track_features["valence"]
        tempo = track_features["tempo"]

        feature_obj = {
            "artist": artist,
            "artist_id": artist_id,
            "popularity": popularity,
            "track_name": track_name,
            "danceability": danceability,
            "energy": energy,
            "loudness": loudness,
            "speechiness": speechiness,
            "acousticness": acousticness,
            "instrumentalness": instrumentalness,
            "valence": valence,
            "tempo": tempo,
        }
        return artist, feature_obj

    except Exception as e:
        print(f"Exception:  {e}")
        return None


# Below modules deals with uploading newly recommended tracks to model
def get_bulk_track_features(track_list):
    try:
        if len(track_list) > 0:
            new_tracks = []
            # Filter tracks that are not already available in TrackFeatures model
            for track in track_list:
                is_exists = TrackFeatures.objects.filter(track_id=track).exists()
                if not is_exists:
                    new_tracks.append(track)
            sp = spotify_callback()
            tracks_other_details = get_bulk_track_id_popularity_name_uri_artist_name(new_tracks)
            track_other_details_list = []
            for track in tracks_other_details['tracks']:
                obj = get_track_id_popularity_name_uri_artist_name(track)
                track_other_details_list.append(obj)
            tracks_features = sp.audio_features(new_tracks)
            features_list = []
            artist_list = []
            for i in range(len(tracks_features)):
                track = tracks_features[i]
                other = track_other_details_list[i]
                artist, obj = get_track_id_features(track, other)
                features_list.append(obj)
                artist_list.append(artist)
            upload_bulk_into_track_features(new_tracks, artist_list, features_list)
            return JsonResponse({"code": 1, "features": features_list})
    except Exception as e:
        print(f"Error in getting bulk features from API: {e}")
        return JsonResponse({"code": -1, "message": e})


def upload_bulk_into_track_features(track_list, artist_list, features_list):
    try:
        # Create a list of TrackFeatures objects using bulk_create
        track_features_list = [
            TrackFeatures(track_id=track_id, artist=artist, features=features)
            for track_id, artist, features in zip(track_list, artist_list, features_list)
        ]

        # Use bulk_create to insert the records into the database in a single query
        # with transaction.atomic():  # For time being neglect atomic
        TrackFeatures.objects.bulk_create(track_features_list)
        update_bulk_track_update_all_save_method(track_list)
    except Exception as e:
        print(f"Error in uploading bulk tracks to TrackFeatures model: {traceback.format_exc()}")


def update_bulk_track_img(track_list):
    if len(track_list) > 0:
        no_img_list = list(TrackFeatures.objects.filter(track_img=None).values_list('track_id', flat=True))
        updated_list = get_track_images_list(no_img_list)
        for track in updated_list:
            TrackFeatures.objects.filter(track_id=track["track_id"]).update(track_img=track["track_image_url"])


def update_bulk_track_update_all_save_method(track_list):
    if len(track_list) > 0:
        tracks = TrackFeatures.objects.filter(track_id__in=track_list)
        for track in tracks:
            track.save()


def get_track_images_list(track_list):
    sp = spotify_callback()
    try:
        tracks = []
        for _ in range(0, math.ceil(len(track_list) / 50)):
            tracks_temp = sp.tracks(track_list[:50])
            del track_list[:50]
            tracks.extend(tracks_temp['tracks'])
        track_info_list = []
        for track in tracks:
            # Extract relevant information from each track
            track_info = {
                'track_id': track['uri'],
                'track_name': track['name'],
                'track_image_url': track['album']['images'][1]['url'] if track['album']['images'] else
                track['album']['images'][0]['url'] if track['album']['images'] else None,
                # Add more fields as needed
            }
            track_info_list.append(track_info)
        return track_info_list
    except Exception as e:
        print(f"Error in get_track_images_list: {e}")
        return []


def get_recommendations_offline_ml(request):
    # data = recommend_tracks_offline_collaborative_filtering()
    # return JsonResponse({"data": data})
    user_tracks = list(
        TrackFeatures.objects.filter(userinterestedtracks__username__username='harsha').values("track_id", "features"))
    query = ~Q(features__in=user_tracks)
    all_tracks = list(TrackFeatures.objects.filter(query).values('track_id', 'features'))
    recommend_tracks_offline(user_tracks, all_tracks)
    df = pd.DataFrame([track['features'] for track in user_tracks])
    df = df.get(["tempo", "energy", "valence", "loudness", "danceability"])
    return JsonResponse({"all": all_tracks, "user": user_tracks})
