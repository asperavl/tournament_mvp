from django.db import models
from django.db.models.signals import post_delete,pre_delete
from django.dispatch import receiver

from django.contrib.auth.models import User




class Tournament(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    max_teams = 4  # Set a reasonable default limit
    status = models.CharField(
        default='available',
        max_length=10,
        choices=[
            ('available', 'Available'),
            ('ongoing', 'Ongoing'),
            ('completed', 'Completed')
        ]
    )
    num_teams_registered = models.IntegerField(default=0)  # Track how many teams have registered
    users = models.ManyToManyField(User, related_name='registered_tournaments', blank=True,null=True)
    def __str__(self):
        return self.name

@receiver(pre_delete, sender=Tournament)
def remove_users_from_tournament(sender, instance, **kwargs):
    # Disassociate all users from the tournament
    instance.users.clear()

class Team(models.Model):
    name = models.CharField(max_length=255)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    players = models.CharField(max_length=1024,null=True, blank=True)

    def save(self, *args, **kwargs):
        # Check if it's a new team (not updating an existing one)
        is_new = self._state.adding

        super().save(*args, **kwargs)  # Save the team first

        if is_new:  # If it's a new registration, update num_teams_registered
            self.tournament.num_teams_registered += 1
            self.tournament.save()


    def __str__(self):
        return f"{self.name} - {self.tournament.name}"
    

@receiver(post_delete, sender=Team)
def update_num_teams_registered(sender, instance, **kwargs):
    tournament = instance.tournament
    tournament.num_teams_registered -= 1
    tournament.save()


class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    team1 = models.ForeignKey(Team, related_name='team1', on_delete=models.CASCADE)
    team2 = models.ForeignKey(Team, related_name='team2', on_delete=models.CASCADE)
    score1 = models.IntegerField(null=True, blank=True)
    score2 = models.IntegerField(null=True, blank=True)
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="won_matches")
    round_number = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.team1.name} vs {self.team2.name}"
