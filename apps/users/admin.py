from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html

from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('display_avatar', 'phone_number', 'full_name', 'is_student', 'is_staff', 'date_joined',)
    list_filter = ('is_student', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('phone_number', 'full_name')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('phone_number', 'full_name')}),
        ('Аватар', {'fields': ('avatar',)}),
        ('Разрешения', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_student')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    def display_avatar(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.avatar.url)
        return "Нет аватара"

    display_avatar.short_description = 'Аватар'


admin.site.unregister(Group)
admin.site.site_header = "Администрация"
admin.site.site_title = "Администрация"
admin.site.index_title = "Добро пожаловать в ТУИТ Логопед"
