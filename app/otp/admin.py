from django.contrib import admin
from .models import OTP


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ("mobile", "code", "is_verified", "created_at", "expires_at")
    list_filter = ("is_verified", "created_at")
    search_fields = ("mobile", "code")
    readonly_fields = ("code", "created_at", "expires_at")

    def has_add_permission(self, request):
        # Prevent manual OTP creation from admin
        return False
