import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from collections import Counter

import numpy as np

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

from .models import UserInterestedTracks
from django.db.models import Count


def most_listened_artists(tracks):
    artist_ids = [track['features']['artist_id'] for track in tracks]

    # Use Counter to count occurrences of each artist ID
    artist_id_counts = Counter(artist_ids)

    # Find the most common artist IDs and their counts
    most_common_artist_ids = artist_id_counts.most_common()
    sorted_artist_ids = sorted(most_common_artist_ids, key=lambda x: x[1], reverse=True)
    return sorted_artist_ids


def get_top_5_artists(artists_list):
    sorted_array = []
    for artist_id, count in artists_list:
        if len(sorted_array) > 5:
            break
        sorted_array.append(artist_id)
    return sorted_array


def get_recommended_tracks_features_ml(tracks):
    df = pd.DataFrame([track['features'] for track in tracks])
    sorted_artist_list = most_listened_artists(tracks)
    top_5_artists = get_top_5_artists(sorted_artist_list)

    df = df.get(["tempo", "energy", "valence", "loudness", "danceability"])
    feature_columns = ["tempo", "energy", "valence", "loudness", "danceability"]
    mean_features = df.mean()
    return top_5_artists, dict(mean_features)


def outliers_z_score(data):
    data = data['popularity']
    # Z-Score
    mean = np.mean(data)
    std = np.std(data)
    outliers = []
    threshold = 3
    print(f"Mean: {mean}\tSTD: {std}")
    for i in data:
        z_score = (i - mean) / std
        print(f"Data: {i} Z: {z_score}")
        if np.abs(z_score) > threshold:
            outliers.append(i)
    print(outliers)


# Below module is used for collaborative filtering which mean if two users interact with same tracks and
# some other tracks too then we recommend there other tracks to other user

def get_user_based_collaborative_filter_tracks(user):
    try:
        min_common_tracks = 1
        user_tracks = list(
            UserInterestedTracks.objects.filter(username=user).values_list('track_id', flat=True))
        # Get list of user that have common interested tracks with target user
        other_common_users = list(UserInterestedTracks.objects.filter(track_id__in=user_tracks)
                                  .annotate(common_tracks=Count('track_id'))
                                  .filter(common_tracks__gte=min_common_tracks)
                                  .exclude(username__username=user)
                                  .values_list('username__username', flat=True))
        # Get tracks lists that listed by all other similar users
        tracks_recommended = list()
        other_users_len = len(other_common_users)
        for i in range(3 if other_users_len > 3 else other_users_len, -1, -1):
            similar_tracks = list(UserInterestedTracks.objects.filter(username__username__in=other_common_users)
                                  .exclude(track_id__in=user_tracks)
                                  .annotate(user_count=Count('username__username'))
                                  .filter(user_count__gt=i)
                                  .values_list('track_id', flat=True)
                                  )
            tracks_recommended.extend(similar_tracks)
            tracks_recommended = list(set(tracks_recommended))
            if len(tracks_recommended) > 10:
                return tracks_recommended
            else:
                user_tracks.extend(similar_tracks)
        return tracks_recommended
    except Exception as e:
        print(f"Exception in getting collaborative_filter_features: {e}")
        return []


def recommend_tracks_offline_collaborative_filtering(user):
    users = get_user_based_collaborative_filter_tracks(user)
    return users


def recommend_tracks_offline(user_tracks, all_tracks):
    # Collaborative filtering user based
    user_based_recommended_tracks = get_user_based_collaborative_filter_tracks(user)
    return user_based_recommended_tracks
