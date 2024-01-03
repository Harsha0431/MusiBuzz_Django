import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from collections import Counter

import numpy as np


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


def get_recommended_tracks_ml(tracks):
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
        z_score = (i-mean)/std
        print(f"Data: {i} Z: {z_score}")
        if np.abs(z_score) > threshold:
            outliers.append(i)
    print(outliers)
