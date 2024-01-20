from spotify_api.models import TrackFeatures
from .models import UserInterestedTracks

import random


def add_tracks_to_interested_list(user, track_list):
    for track in track_list:
        is_exist = UserInterestedTracks.objects.filter(username=user, track_id=track).exists()
        if not is_exist:
            track_instance, created = TrackFeatures.objects.get_or_create(track_id=track)
            # Create UserInterestedTracks instance linking the user and track
            if created:
                UserInterestedTracks.objects.create(username=user, track_id=track_instance)


def get_track_ids_from_obj_list(track_list):
    track_list_ids = [track["track_id"] for track in track_list]
    return track_list_ids


# Below module returns tracks from model based on below params(seed artists and track features)
def get_default_recommended_list(top_5_artists, features):
    artist_seed_tracks = list(TrackFeatures.objects.filter(features__artist_id__in=top_5_artists).values("track_id"))
    features_seed_tracks = list(TrackFeatures.objects.filter(
                            features__tempo__gt=features["tempo"], features__energy__gt=features["energy"],
                            features__danceability__gt=features["danceability"]
                ).values("track_id"))
    if features_seed_tracks is None and artist_seed_tracks is None:
        all_tracks_list = list(TrackFeatures.objects.filter().all().values("track_id"))
        all_tracks_list = get_track_ids_from_obj_list(all_tracks_list)
        random.shuffle(all_tracks_list)
        if len(all_tracks_list) > 25:
            return all_tracks_list[:25]
        return all_tracks_list
    combined_tracks = features_seed_tracks + artist_seed_tracks
    track_list_ids = get_track_ids_from_obj_list(combined_tracks)
    # To remove duplicate values
    track_list_ids = list(set(track_list_ids))
    if len(track_list_ids) > 25:
        return track_list_ids[:25]
    return track_list_ids
