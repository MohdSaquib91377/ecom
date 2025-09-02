

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from config.base import TimeStampModel
from accounts.managers import UserManager

class User(AbstractBaseUser, PermissionsMixin,TimeStampModel):
    mobile = models.CharField(max_length=10, null=True, blank=True, unique=True)
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


class Address(TimeStampModel):
    ADDRESS_TYPE_CHOICES = (
        ("HOME", "Home (All day delivery)"),
        ("WORK", "Work (Delivery between 10 AM - 5 PM)"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    alternate_phone = models.CharField(max_length=10, blank=True, null=True)
    pincode = models.CharField(max_length=10)
    locality = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField()  # Full street + area address
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default="HOME")
    is_default = models.BooleanField(default=False)

 

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.address_type}"
