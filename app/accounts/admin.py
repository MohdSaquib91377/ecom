from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User,Address

class UsersAdmin(UserAdmin):
    model = User
    list_display = ('id','mobile','is_mobile_verified', 'is_staff', 'is_active')
    list_filter = ('mobile', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('mobile', 'password',"is_mobile_verified")}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('mobile',)
    ordering = ('mobile',)


admin.site.register(User, UsersAdmin)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "phone",
        "city",
        "state",
        "address_type",
        "is_default",
        "created_at",
    )
    list_filter = ("address_type", "city", "state", "is_default")
    search_fields = ("name", "phone", "city", "state", "pincode", "address")
    ordering = ("-created_at",)