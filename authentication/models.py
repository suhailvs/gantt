from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    USER_TYPE_CHOICES = (
      (1, 'administrator'), #admin, superadmin etc, so ./manage.py createsuperuser will return default
      (2, 'creator'),
      (3, 'departmental_creator'),
      (4, 'viewer'),
      (5, 'others'),
    )
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES,default=1)

    @property
    def is_administrator(self):
        return self.user_type == 1

    @property
    def is_creator(self):
        "Is the user a creator?"
        return self.user_type == 2

    @property
    def is_departmental_creator(self):
        return self.user_type == 3

    @property
    def is_viewer(self):
        return self.user_type == 4