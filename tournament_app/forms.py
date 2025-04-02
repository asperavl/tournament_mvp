from django import forms
from .models import Team

class TeamRegistrationForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'players']  # Include both fields

    # Customize the players field (optional)
    players = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Player One, Player Two, Player Three...'
        }),
        help_text="Enter player names separated by commas"
    )

    def clean_players(self):
        """Basic validation - ensure at least one player is entered"""
        players = self.cleaned_data.get('players', '').strip()
        if not players:
            raise forms.ValidationError("Please enter at least one player name")
        return players