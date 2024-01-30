from django.urls import path
from . import views

from .helpers_bulk import get_recommendations_offline_ml
from . import playlists_with_data

urlpatterns = [
    path('playlist/create/', views.create_playlist, name="create_playlist"),
    path('playlist/add_track/', views.add_track_to_playlist, name="add_track_to_playlist"),
    path('liked/add_track/', views.add_track_to_liked_list, name="add_track_to_liked_list"),
    path('liked/remove_track/', views.remove_track_from_liked_list, name="remove_track_from_liked_list"),
    path('interested/add_track/', views.add_track_to_interested_list, name="add_track_to_interested_list"),
    path('liked/list/', views.get_liked_tracks_list, name="user_liked_tracks_list"),
    path('interested/list/', views.get_interested_tracks_list, name="interested_tracks_list"),
    path('recommended/list/', views.get_recommended_list, name="get_recommended_tracks_list"),
    path('list_preview/', views.get_listed_tracks_full_details, name="get_listed_tracks_full_list"),
    # Test URLs
    path('test/list', get_recommendations_offline_ml, name="TEST recommendation offline"),

    # Playlist lists with complete data
    path('playlist/preview/data/', playlists_with_data.track_list_data, name='get_liked_list_with_data')
]
