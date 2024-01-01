import json
from django.http import JsonResponse

import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from .credentials import client_ID, client_SECRET, scope, redirect_URI


def spotify_callback():
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_ID, client_secret=client_SECRET))
    access_token = sp.auth_manager.get_access_token(as_dict=False)
    return sp


def get_id_from_track_id(track_id):
    track_id_only = track_id.split(':')[2]
    return track_id_only


def get_track_id_popularity_name_uri_artist_name(track_id):
    try:
        sp = spotify_callback()
        track_info = sp.track(track_id)
        artist_obj = track_info['artists'][0]
        track_obj = track_info
        track_id = track_obj['id']
        track_name = track_obj['name']
        track_uri = track_obj['uri']
        popularity = track_obj['popularity']
        artist_name = artist_obj['name']
        json_obj = {"track_id": track_id, "track_name": track_name, "track_uri": track_uri,
                    "popularity": popularity, "artist_name": artist_name}
        return json_obj

    except Exception as e:
        print(f"Exception:  {e}")
        return None


def get_track_id_features(track_id):
    try:
        sp = spotify_callback()
        track_only_id = get_id_from_track_id(track_id)
        analysis = sp.audio_features(track_only_id)
        track_features = analysis[0]
        track_popularity_artist = get_track_id_popularity_name_uri_artist_name(track_only_id)
        artist = track_popularity_artist["artist_name"]
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
        return feature_obj

    except Exception as e:
        print(f"Exception:  {e}")
        return None

