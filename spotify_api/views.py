from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import requests
from .credentials import client_ID, client_SECRET, scope, redirect_URI
from . import helpers


@parser_classes([JSONParser])
def login(request):
    # Create a SpotifyOAuth object
    sp_oauth = SpotifyOAuth(client_id=client_ID, client_secret=client_SECRET, redirect_uri=redirect_URI, scope=scope)

    # Print the sp_oauth object to the console
    print("\n\nSP_OAuth Object:", sp_oauth, "\n\n")

    # Redirect the user to the Spotify login page
    # Get the authorization URL
    url = sp_oauth.get_authorize_url()
    # Print the authorization url to the console
    print(url)

    # Redirect the user to the Spotify login page
    return HttpResponseRedirect(url)


# Module to OAuth
def callback(request):
    # Create a SpotifyOAuth object
    sp_oauth = SpotifyOAuth(client_id=client_ID, client_secret=client_SECRET, redirect_uri=redirect_URI, scope=scope)

    # Get the authorization code from the query parameters
    code = request.GET.get("code")

    # Request an access token using the authorization code
    token_info = sp_oauth.get_access_token(code)

    # Extract the access token
    access_token = token_info["access_token"]
    refresh_token = token_info['refresh_token']

    # Store the access token in a secure way (e.g. in a session or database)
    request.session["access_token"] = access_token

    # Redirect the user to the top tracks page
    return JsonResponse({"at": access_token, "rt": refresh_token})


def spotify_callback():
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_ID, client_secret=client_SECRET))
    access_token = sp.auth_manager.get_access_token(as_dict=False)
    return sp


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def get_track(request):
    search_str = request.GET.get('search', None)
    if not search_str:
        return JsonResponse({"code": -1, "message": 'Give keyword to search'})
    sp = spotify_callback()
    track_info = sp.search(q=search_str, type=['track'])
    # for track in track_info['albums']['items']:
    #     if 'available_markets' in track:
    #         del track['available_markets']
    track_id = track_info['tracks']['items'][0]['id']
    sp_track = helpers.get_track_id_popularity_name_uri_artist_name(track_id)
    return JsonResponse(sp_track)


@api_view(["GET"])
def get_top_tracks(request):
    if request.method == 'GET':
         # Get the access token from the session
        access_token = request.session.get("access_token")
        print('\n\n ACCESS TOKEN: ', access_token, '\n\n')

        # Create a Spotipy client using the access token
        sp = spotipy.Spotify(auth=access_token)

        # Make a request to the Spotify API to retrieve the user's profile information
        response = sp.me()

        # Check if the request was successful
        if response is not None:
            # The access token is valid
            print("The access token is valid.\n\n")
        else:
            # The access token is invalid or has expired
            print("The access token is invalid or has expired.\n\n")

        # Set the username
        # username = credentials.username

        # Make the HTTP GET request to the Spotify API
        response = sp.current_user_top_tracks(limit=50, offset=0, time_range="medium_term")

        # Extract the top tracks from the response
        top_tracks = response["items"]

         # Create a list of dictionaries representing the top tracks
        tracks = []
        for track in top_tracks:
            track_info = {
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "album": track["album"]["name"],
            }
            tracks.append(track_info)

        # print tracks list to console
        print("\n\n\n\nLIST OF TRACKS:", tracks)

        return JsonResponse(tracks, safe=False)

    else:
        error = "An error has occurred"
        return error
