from django.urls import path

from apps.users.views import (
    LandingPageView, RegisterView, LoginView, VerifyCodeView, ResendCodeView,
    DashboardView, SettingsView, ChangePhoneView, HelpView, LogoutView,
    DeleteAccountView, SetFullNameView, UpdateAvatarView, VerifyPhoneChangeView,
    DeleteAvatarView
)

urlpatterns = [
    path('', LandingPageView.as_view(), name='landing'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify_code'),
    path('set-fullname/', SetFullNameView.as_view(), name='set_fullname'),
    path('resend-code/', ResendCodeView.as_view(), name='resend_code'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('update-avatar/', UpdateAvatarView.as_view(), name='update_avatar'),
    path('delete-avatar/', DeleteAvatarView.as_view(), name='delete_avatar'),
    path('change-phone/', ChangePhoneView.as_view(), name='change_phone'),
    path('verify-phone-change/', VerifyPhoneChangeView.as_view(), name='verify_phone_change'),
    path('help/', HelpView.as_view(), name='help'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete_account'),
]
