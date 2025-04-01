from django import forms
from .models import Team

class TeamRegistrationForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'players']  # Add the fields you want to include in the form

    # Customize the 'players' field to accept multiple player names as a comma-separated string
    players = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Enter players separated by commas'})
    )
