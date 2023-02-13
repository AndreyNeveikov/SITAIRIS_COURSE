import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from core.constants import Roles
from .managers import CustomUserManager


class User(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    image = models.CharField(max_length=200, null=True, blank=True)
    role = models.CharField(max_length=9, choices=Roles.choices,
                            default=Roles.USER.value, blank=False)
    title = models.CharField(max_length=80)
    is_blocked = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.role} {self.username}"
