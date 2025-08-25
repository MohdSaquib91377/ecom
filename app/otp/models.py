import uuid
import random
from datetime import timedelta
from django.db import models
from django.utils import timezone
from config.base import TimeStampModel

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))


class OTP(TimeStampModel):
    mobile = models.CharField(max_length=10)
    code = models.CharField(max_length=6, default=generate_otp)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # If no expiry is set, default 5 minutes from now
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def verify(self, code: str) -> bool:
        """Check if OTP matches and is valid"""
        if self.is_verified:
            return False  # Already used
        if self.is_expired():
            return False
        if self.code == code:
            self.is_verified = True
            self.save(update_fields=["is_verified"])
            return True
        return False

    def __str__(self):
        return f"OTP for {self.mobile} - {self.code}"
