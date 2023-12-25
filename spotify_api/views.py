from django.shortcuts import redirect
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from .credentials import scope, redirect_URI, client_ID, client_SECRET
# Models
from .models import SpotifyToken


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def spotify_callback(request):
    username = request.get('username')

    if not username or not code:
        return JsonResponse({"code": -1, "message": "Invalid request data"})
    sp_oauth = SpotifyOAuth(client_ID, client_SECRET, redirect_URI,
                            scope=scope)

    token_info = sp_oauth.get_access_token(request.GET['code'])

    if 'access_token' not in token_info:
        return JsonResponse({"code": -1, "message": "Failed to obtain access token"})

    # Save token_info in the user's session or database for later use
    SpotifyToken.objects.update_or_create(
        user=username,
        defaults={'access_token': token_info['access_token'], 'refresh_token': token_info['refresh_token']}
    )

    return JsonResponse({"code": 1, "message": "Access token created successfully"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def refresh_spotify_token(request):
    user = request.get('username')
    try:
        spotify_token = SpotifyToken.objects.get(username=user)
    except SpotifyToken.DoesNotExist:
        return JsonResponse({"code": -1, "message": "No Spotify token found for the user"})

    # Use the refresh token to obtain a new access token
    sp_oauth = SpotifyOAuth(client_ID, client_SECRET, redirect_URI, scope=scope)
    token_info = sp_oauth.refresh_access_token(spotify_token.refresh_token)

    if 'access_token' not in token_info:
        return JsonResponse({"code": -1, "message": "Failed to refresh access token"})

    # Update the existing SpotifyToken with the new access token
    spotify_token.access_token = token_info['access_token']
    spotify_token.save()

    return JsonResponse({"code": 1, "message": "Access token refreshed successfully"})
