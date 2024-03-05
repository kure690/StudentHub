from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class CustomUser(AbstractUser):
    # Add your custom fields here
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
