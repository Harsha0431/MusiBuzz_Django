from django.urls import path

from . import views

urlpatterns = [
    path('signin/', views.login_user),
    path('signup/', views.sign_up, name="add_user"),
    path('verify/token/', views.verify_token, name="verify_user_token")
]
