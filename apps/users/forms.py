from django import forms
from apps.users.models import User


class UserRegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['']
