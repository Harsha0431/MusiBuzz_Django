import json

import requests
from django.http import JsonResponse
from numpy import record
from requests import request

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
        artist_id = artist_obj['id']
        json_obj = {"track_id": track_id, "track_name": track_name, "track_uri": track_uri,
                    "popularity": popularity, "artist_name": artist_name, "artist_id": artist_id}
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
        return feature_obj

    except Exception as e:
        print(f"Exception:  {e}")
        return None


def get_track_id_from_object(track_obj):
    try:
        track_uri = track_obj['uri']
        return track_uri
    except Exception as e:
        print(e)
        return None
    pass


def get_tracks_from_track_list(track_list):
    if len(track_list) > 0:
        track_list = track_list['tracks']
        track_id_list = []
        print(track_list)
        for obj in track_list:
            track_uri = get_track_id_from_object(obj)
            if track_uri is not None:
                track_id_list.append(track_uri)
        return track_id_list


def get_recommended_tracks_target_features(top_5_artists, features, limit):
    sp = spotify_callback()
    access_token = sp.auth_manager.get_access_token(as_dict=False)
    headers = {'Authorization': f'Bearer {access_token}'}
    top_5_artists = top_5_artists[0:2]
    seed_artists = '%2C'.join(top_5_artists)
    endpoint = f'''https://api.spotify.com/v1/recommendations?limit={limit}&seed_artists={seed_artists}&min_energy={features["energy"]}&target_tempo={features["tempo"]}&target_danceability={features["danceability"]}&target_valence={features["valence"]}'''
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        recommendations_data = response.json()
        track_uri_list = get_tracks_from_track_list(recommendations_data)
        return track_uri_list


def get_recommended_tracks_seed_artist(top_5_artists, limit):
    sp = spotify_callback()
    access_token = sp.auth_manager.get_access_token(as_dict=False)
    headers = {'Authorization': f'Bearer {access_token}'}
    top_5_artists = top_5_artists[0:2]
    seed_artists = '%2C'.join(top_5_artists)
    endpoint = f'''https://api.spotify.com/v1/recommendations?limit={limit}&seed_artists={seed_artists}'''
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        recommendations_data = response.json()
        track_uri_list = get_tracks_from_track_list(recommendations_data)
        return track_uri_list


def get_recommended_tracks_mixed(top_5_artists, features):
    recommended_list_seed_artist = get_recommended_tracks_seed_artist(top_5_artists, 10)
    recommended_list_features = get_recommended_tracks_target_features(top_5_artists, features, 10)

    if recommended_list_features is None and recommended_list_seed_artist is None:
        return []
    recommended_list = recommended_list_seed_artist + recommended_list_features

    return recommended_list


def get_top_tracks_list():
    sp = spotify_callback()
    try:
        query = 'songs by anirudh badsha sid sriram arjit hindi telugu tamil'
        track_info = sp.search(query, limit=20, type=['track'], market="IN")
        track_info = track_info['tracks']['items']
        track_list = [track["uri"] for track in track_info]
        return track_list
    except Exception as e:
        print(f"Exception in getting top tracks list in spotify app: {e}")
        return []
