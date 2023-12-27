import json


def get_track_id_popularity_name_uri_artist_name(sp, track_id):
    try:
        track_info = sp.track(track_id)
        return track_info
        artist_obj = track_info['artists'][0]
        track_obj = track_info
        track_id = track_obj['id']
        track_name = track_obj['name']
        track_uri = track_obj['uri']
        popularity = track_obj['popularity']
        artist_name = artist_obj['name']
        json_obj = {"track_id": track_id, "track_name": track_name, "track_uri": track_uri,
                    "popularity": popularity, "artist_name": artist_name}
        return json_obj

    except Exception as e:
        print(f"Exception:  {e}")
        return None
