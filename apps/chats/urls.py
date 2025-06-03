from django.urls import path

from apps.chats.views import ChatListView, ChatDetailView

urlpatterns = [
    path('', ChatListView.as_view(), name='chat_list'),
    path('<int:user_id>/', ChatDetailView.as_view(), name='chat_detail'),
]
