from django.db import models
from django.contrib.auth.models import User


class User_profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    profil_photo = models.ImageField(upload_to="profile_photos/")
    phone_number = models.CharField( max_length=13,)
    address = models.CharField(max_length=100)
