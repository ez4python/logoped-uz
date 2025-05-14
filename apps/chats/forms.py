from django import forms
from apps.chats.models import ChatMessage, HelpRequest


class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message', 'image', 'video', 'file']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'placeholder': 'Введите сообщение...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*'
            }),
            'video': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'video/*'
            }),
            'file': forms.FileInput(attrs={
                'class': 'hidden'
            })
        }


class HelpRequestForm(forms.ModelForm):
    class Meta:
        model = HelpRequest
        fields = ['topic', 'message']
        widgets = {
            'topic': forms.Select(attrs={
                'class': 'form-control'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Опишите вашу проблему или вопрос'
            })
        }
