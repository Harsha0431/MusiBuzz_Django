from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    # path('callback/', views.callback, name='oauth_callback'),
    # path('top-tracks/', views.get_top_tracks, name='oauth_get_top_tracks'),
    path('callback/', views.callback, name='callback'),
    path('search/', views.search, name="search_with_text"),
    path('track/', views.get_track, name='get_track_with_id')
]
