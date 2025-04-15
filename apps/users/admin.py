from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from apps.users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('phone_number', 'first_name', 'last_name', 'is_student', 'is_therapist')
    list_filter = ('is_student', 'is_therapist')
    search_fields = ('phone_number', 'first_name', 'last_name')
    ordering = ('phone_number',)
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'image')}),
        ('Permissions', {'fields': (
            'is_active', 'is_staff', 'is_superuser', 'is_student', 'is_therapist', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone_number', 'first_name', 'last_name', 'password1', 'password2', 'is_student', 'is_therapist')
        }),
    )


admin.site.unregister(Group)
