from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.managers import CustomUserManager


# Create your models here.
class BaseDatetimeModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    phone_number = models.CharField(max_length=20, validators=[], unique=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    # excluded fields
    username = None
    email = None
    groups = None
    objects = CustomUserManager()

    class Meta:
        db_table = "users"
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"

    def __str__(self):
        return self.get_full_name()
