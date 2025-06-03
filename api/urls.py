from django.urls import path

from api.views import UserAuthCodeAPIView

urlpatterns = [
    path('auth/code/', UserAuthCodeAPIView.as_view(), name='auth-code')
]
