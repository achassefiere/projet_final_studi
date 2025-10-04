from django.db import models
from datetime import datetime, timezone
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    pass