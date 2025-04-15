from django.contrib import admin
from apps.chats.models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'message', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('sender__first_name', 'receiver__first_name', 'message')
