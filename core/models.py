from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Represents a customized user class for email/password authentication instead of username/password.
    """
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []