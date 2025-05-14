from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class PhoneNumberForm(forms.Form):
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+998 XX XXX XX XX'
        })
    )


class VerificationCodeForm(forms.Form):
    verification_code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': 'Введите 6-значный код',
            'inputmode': 'numeric',
            'pattern': '[0-9]{6}',
            'autocomplete': 'one-time-code'
        })
    )


class FullNameForm(forms.Form):
    full_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваше полное имя'
        })
    )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'})
        }


class UserAvatarForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'hidden', 'accept': 'image/*'})
        }


class ContactSupportForm(forms.Form):
    SUBJECT_CHOICES = [
        ('technical', 'Техническая проблема'),
        ('account', 'Вопрос по аккаунту'),
        ('course', 'Вопрос по курсу'),
        ('payment', 'Вопрос по оплате'),
        ('other', 'Другое'),
    ]

    subject = forms.ChoiceField(
        choices=SUBJECT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        required=True
    )
