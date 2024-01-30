from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from spotify_api.models import TrackFeatures


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
def track_list_data(request):
    try:
        track_list = request.data['track_list']
        db_list = list(TrackFeatures.objects.filter(track_id__in=track_list).values("track_id", "features",
                                                                                    "track_img", "artist"))
        list_to_send = []
        for data in db_list:
            features = data['features']
            new_data = {
                "track_id": data['track_id'],
                "track_name": features['track_name'],
                "artist_name": data['artist'],
                "artist_id": features['artist_id'],
                "track_image": data['track_img']
            }
            list_to_send.append(new_data)
        return JsonResponse({"code": 1, "data": list_to_send})
    except Exception as e:
        print(f"Exception in getting data of listed data for playlist preview due to {e}")
        return JsonResponse({"code": -1, "message": 'Internal server error'})
