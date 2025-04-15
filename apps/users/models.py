from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.users.managers import CustomUserManager


class User(AbstractUser):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20, unique=True)
    image = models.ImageField(upload_to='user_images/', blank=True, null=True)

    is_student = models.BooleanField(default=False)
    is_therapist = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name']

    # excluded fields
    username = None
    email = None

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.get_full_name()} - ({self.phone_number})"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'users'
