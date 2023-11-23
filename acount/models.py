from django.db import models
from django.contrib.auth.models import User


class User_profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    profil_photo = models.ImageField(upload_to="profile_photos/")
    phone_number = models.CharField( max_length=13,)
    address = models.CharField(max_length=100)


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}'s Wallet"