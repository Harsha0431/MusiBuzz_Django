from django.urls import path
from . import views

urlpatterns = [
    path('playlist/create/', views.create_playlist, name="create_playlist"),
    path('playlist/add_track/', views.add_track_to_playlist, name="add_track_to_playlist"),
]
