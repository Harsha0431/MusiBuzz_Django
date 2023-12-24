from django.db import models

from django.contrib.auth.models import User


# Create your models here.
class Profile(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE, default=None, related_name="profile")
    email = models.EmailField(max_length=255, primary_key=True)
    role = models.CharField(max_length=255, default='user')
