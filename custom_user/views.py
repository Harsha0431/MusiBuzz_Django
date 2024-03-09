from django.http import HttpResponse
import json
from . import models
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from django.db.utils import IntegrityError
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.contrib.auth.models import User


def login_email(request, req_password, req_email):
    user = models.Profile.objects.filter(email=req_email).first()
    username_fetched = user.username
    return authenticate(request, username=username_fetched, password=req_password)


@api_view(["POST"])
@permission_classes([])
@authentication_classes([])  # Exclude authentication for this view
def login_user(request):
    if request.method == 'POST':
        try:
            req_data = json.loads(request.body.decode('utf-8'))
            req_email = req_data.get('email') or ''
            req_password = req_data.get('password')
            req_username = req_data.get('username') or ''

            if req_username != '':
                # Authenticate the user
                user = authenticate(request, username=req_username, password=req_password)
                req_username = user

            else:
                user = models.Profile.objects.filter(email=req_email).first()
                if user is None:
                    return JsonResponse({'code': 0, 'message': 'Invalid credentials'})
                print(user)
                req_username = user.username
                user = authenticate(request, username=req_username, password=req_password)

            if user is not None:
                # Login the user
                login(request, user)
                token, _ = Token.objects.get_or_create(user=user)
                user_obj = models.Profile.objects.filter(username=req_username).first()
                user_data = {
                    'username': user_obj.username.username,
                    'email': user_obj.email,
                    'role': user_obj.role
                }
                data = {'code': 1, "user": user_data, "token": token.key, 'message': "Logged in successfully"}
                return JsonResponse(data)
            else:
                return JsonResponse({'code': 0, 'message': 'Invalid credentials'})

        except Exception as e:
            print(f"Login Error: {e}")
            return HttpResponse(json.dumps({"code": -1, "message": "Internal server error"}))


@api_view(["POST"])
@permission_classes([])
@authentication_classes([])  # Exclude authentication for this view
def sign_up(request):
    try:
        req_data = json.loads(request.body.decode('utf-8'))
        username = req_data.get('username')
        email = req_data.get('email')
        password = req_data.get('password')
        role = req_data.get('role') or 'user'
        if username and email and password:
            user_filter_email = User.objects.filter(email=email).first()
            if user_filter_email is not None:
                return JsonResponse({"code": 0, "message": "Email already exists"})
            user = User.objects.create_user(username=username, password=password, email=email)
            user_profile = models.Profile.objects.create(username=user, email=email, role=role)
            user_profile.save()
            user.save()
            return JsonResponse({"code": 1, "message": "User created successfully"})
        else:
            return JsonResponse({"code": 0, "message": "Incomplete data to register"})
    except IntegrityError as e:
        if "UNIQUE constraint failed: auth_user.username" in str(e):
            return JsonResponse({"code": 0, "message": "Username already exists"})
        elif "UNIQUE constraint failed: auth_user.email" in str(e):
            user_to_delete = User.objects.get(username=ureq_data.get('username'))
            user_to_delete.delete()
            return JsonResponse({"code": 0, "message": "Email already exists"})
    except Exception as e:
        print(f"Sign Up Error: {e}")
        return HttpResponse(json.dumps({"code": -1, "message": "Internal server error"}))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def verify_token(request):
    try:
        user = request.user
        if user is not None:
            user_data = models.Profile.objects.filter(username=user).first()
            user_obj = {
                'username': user_data.username.username,
                'email': user_data.email,
                'role': user_data.role,
            }
            return JsonResponse({"code": 1, "user": user_obj})
        else:
            return JsonResponse({"code": 0, "message": 'Invalid token'})
    except Exception as e:
        print(f"Error in token validation: {e}")
        return JsonResponse({"code": -1, "message": "Internal server error"})
