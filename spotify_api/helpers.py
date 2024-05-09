import json
import random

import requests
from django.http import JsonResponse
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
        track_album = track_info['album']['images'][0]
        track_img = track_album['url']
        artist_obj = track_info['artists'][0]
        # Get artist obj from spotify for image
        artist_spo = sp.artist(artist_id=artist_obj['id'])
        artist_image = artist_spo['images']
        artist_image = artist_image[0]['url'] if len(artist_image) > 0 else track_img
        track_obj = track_info
        track_id = track_obj['id']
        track_name = track_obj['name']
        track_uri = track_obj['uri']
        popularity = track_obj['popularity']
        artist_name = artist_obj['name']
        artist_id = artist_obj['id']
        json_obj = {"track_id": track_id, "track_name": track_name, "track_uri": track_uri,
                    "popularity": popularity, "artist_name": artist_name, "artist_img": artist_image,
                    "artist_id": artist_id, "track_img": track_img}
        return json_obj

    except Exception as e:
        print(f"Exception in get_track_id_popularity_name_uri_artist_name of helper:  {e}")
        return None


def get_track_id_features(track_id):
    try:
        sp = spotify_callback()
        track_only_id = get_id_from_track_id(track_id)
        analysis = sp.audio_features(track_only_id)
        track_features = analysis[0]
        track_popularity_artist = get_track_id_popularity_name_uri_artist_name(track_only_id)
        track_img = track_popularity_artist['track_img']
        artist = track_popularity_artist["artist_name"]
        artist_img = track_popularity_artist['artist_img']
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
            "track_img": track_img,
            "danceability": danceability,
            "energy": energy,
            "loudness": loudness,
            "speechiness": speechiness,
            "acousticness": acousticness,
            "instrumentalness": instrumentalness,
            "valence": valence,
            "tempo": tempo,
            "artist_img": artist_img
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
        query = 'hindi top 100'
        offset = random.randint(1, 10)
        track_info = sp.search(query, limit=20, offset=offset, type=['track'], market="IN")
        track_info = track_info['tracks']['items']
        track_list = [track["uri"] for track in track_info]
        return track_list
    except Exception as e:
        print(f"Exception in getting top tracks list in spotify app: {e}")
        return []


def process_search_query(search_req, type_req, limit_req, offset_req):
    try:
        sp = spotify_callback()
        track_info = sp.search(q=search_req, type=type_req, offset=offset_req, limit=limit_req)
        return track_info
    except Exception as e:
        print(f"Exception in processing search query due to a {e}")
        return []


def process_artist_related_tracks_search(artist_id):
    try:
        sp = spotify_callback()
        track_info = sp.artist_top_tracks(artist_id)
        return track_info
    except Exception as e:
        print(f"Exception in processing search query due to a {e}")
        return []


def filter_tracks_from_artist_related_tracks_obj(track_list):
    filtered_list = list()
    for track in track_list:
        track = track['album']
        img_list = track['images']
        image = img_list[0]['url'] if len(img_list) > 0 else ''
        total_tracks = track['total_tracks'] if track['type'] == 'album' else -1
        track_number = -1
        name = track['name']
        uri = track['uri']
        track_obj = {
            "name": name,
            "image": image,
            "type": track['type'],
            "total_tracks": total_tracks,
            "track_number": track_number,
            "uri": uri
        }
        filtered_list.append(track_obj)
    return filtered_list


# This module deals with filtering artists list from artists_related_artists (with seed artist)
def process_list_to_fetch_suggested_artist(artist_list):
    artist_list = artist_list["artists"]
    new_artist_list = []
    for item in artist_list:
        followers = item['followers']['total'] or 'Not Available'
        img_list = item['images']
        if len(img_list) > 0:
            image = item['images'][0]['url']
        else:
            image = ''
        name = item['name']
        artist_id = item['id']
        obj = {"artist": name, "followers": followers, "artist_id": artist_id, "artist_img": image}
        new_artist_list.append(obj)
    return new_artist_list


def fetch_suggested_artists_seed(seed_artist):
    artist_list = list()
    try:
        sp = spotify_callback()
        artist_list = sp.artist_related_artists(seed_artist)
        artist_list = process_list_to_fetch_suggested_artist(artist_list)
        return artist_list
    except Exception as e:
        print(f"Error in getting suggested artists from spotify due to {e}")
        return artist_list


def fetch_suggested_artists_random_top():
    pass
