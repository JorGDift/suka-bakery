from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('name', 'last_name', 'mail', 'phone', 'is_active', 'is_staff')
    search_fields = ('name', 'last_name', 'mail')
    list_filter = ('is_active', 'is_staff')
    ordering = ('-created',)

    fieldsets = (
        (None, {'fields': ('mail', 'password')}),
        ('Información Personal', {'fields': ('name', 'last_name', 'phone', 'avatar')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mail', 'name', 'last_name', 'password1', 'password2'),
        }),
    )