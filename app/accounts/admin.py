from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

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
