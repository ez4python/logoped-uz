from django import forms


class FeedbackForm(forms.Form):
    feedback = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        label='Fikr-mulohaza'
    )
    mark = forms.IntegerField(
        required=True,
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Baho'
    )
