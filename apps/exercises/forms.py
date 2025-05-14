from django import forms

from apps.exercises.models import Submission


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['audio_answer', 'text_answer']
        widgets = {
            'audio_answer': forms.FileInput(attrs={'accept': 'audio/*', 'class': 'hidden'}),
            'text_answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['feedback', 'mark']
        widgets = {
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'mark': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
        }
