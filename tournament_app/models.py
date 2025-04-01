from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.text import slugify

class Tournament(models.Model):
    name = models.CharField(max_length=255)
    status = models.CharField(
        default='available',
        max_length=10,
        choices=[
            ('available', 'Available'),
            ('ongoing', 'Ongoing'),
            ('completed', 'Completed')
        ]
    )
    num_teams_registered = models.IntegerField(default=0)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def is_full(self):
        return self.num_teams_registered >= 4  # Hardcoded 4-team limit

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=255)
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE)
    registered_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='registered_teams'  # Important for reverse lookups
    )
    class Meta:
        unique_together = [('tournament', 'registered_by')]  # 1 team per user per tournament

    def save(self, *args, **kwargs):
        is_new = not self.pk  # Check if this is a new team
        
        super().save(*args, **kwargs)  # Save the team first

        if is_new:
            # Update tournament counters
            self.tournament.num_teams_registered += 1
            
            # Automatically start tournament when 4 teams register
            if self.tournament.num_teams_registered >= 4:
                self.tournament.status = 'ongoing'
            
            self.tournament.save()

    def __str__(self):
        return f"{self.name} ({self.tournament})"

class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    team1 = models.ForeignKey(Team, related_name='team1_matches', on_delete=models.CASCADE)
    team2 = models.ForeignKey(Team, related_name='team2_matches', on_delete=models.CASCADE)
    team1_score = models.PositiveIntegerField(null=True, blank=True)
    team2_score = models.PositiveIntegerField(null=True, blank=True)
    winner = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL)
    round_number = models.PositiveIntegerField(default=1)  # 1=Semifinals, 2=Finals

    def clean(self):
        # Basic validation - teams must be from same tournament
        if self.team1.tournament != self.team2.tournament:
            raise ValidationError("Teams must be from the same tournament")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Mark tournament as completed if final has a winner
        if self.round_number == 2 and self.winner:
            self.tournament.status = 'completed'
            self.tournament.save()

    def __str__(self):
        return f"{self.team1} vs {self.team2} (Round {self.round_number})"