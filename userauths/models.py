# userauths/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass  # Add any custom fields or methods here
