

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from config.base import TimeStampModel
from accounts.managers import UserManager

class User(AbstractBaseUser, PermissionsMixin,TimeStampModel):
    mobile = models.BigIntegerField(null=True, blank=True,unique=True)
    is_mobile_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.mobile}"

    class Meta:
        ordering = ["-id"]
