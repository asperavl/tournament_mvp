from django.shortcuts import render, redirect, get_object_or_404
from .models import Tournament, Team, Match
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .forms import TeamRegistrationForm
from django.contrib import messages
from django.db import models;

def index(request):
    tournaments = Tournament.objects.all()
    return render(request, 'index.html', {'tournaments': tournaments})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def register_team(request, tournament_slug):
    tournament = get_object_or_404(Tournament, slug=tournament_slug)

    # Block registration if tournament isn't available
    if tournament.status != 'available':
        messages.error(request, "This tournament has already started")
        return redirect('dashboard')

    # Block if user already registered
    if Team.objects.filter(tournament=tournament, registered_by=request.user).exists():
        messages.error(request, "You can only register one team per tournament")
        return redirect('dashboard')

    # Block if tournament is full
    if tournament.num_teams_registered >= 4:
        messages.error(request, "Tournament is full (4 teams maximum)")
        return redirect('dashboard')

    if request.method == 'POST':
        form = TeamRegistrationForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.tournament = tournament
            team.registered_by = request.user
            team.save()  # This triggers the status update in Team.save()
            
            messages.success(request, f"Team '{team.name}' registered successfully!")
            return redirect('dashboard')
    else:
        form = TeamRegistrationForm()

    return render(request, 'register_team.html', {
        'form': form,
        'tournament': tournament,
        'spots_remaining': 4 - tournament.num_teams_registered
    })

@login_required
def dashboard(request):
    # Get tournaments where user has teams with count annotation
    registered_tournaments = Tournament.objects.filter(
        team__registered_by=request.user
    ).annotate(
        user_team_count=models.Count('team')
    ).distinct()
    
    # Get available tournaments user hasn't joined
    available_tournaments = Tournament.objects.filter(
        status='available'
    ).exclude(
        team__registered_by=request.user
    )

    # Get total teams for current user
    user_team_count = Team.objects.filter(registered_by=request.user).count()

    return render(request, 'dashboard.html', {
        'registered_tournaments': registered_tournaments,
        'available_tournaments': available_tournaments,
        'user_team_count': user_team_count,
        'debug' : False
    })


@login_required
def view_tournament_bracket(request, tournament_slug):
    tournament = get_object_or_404(Tournament, slug=tournament_slug)
    matches = Match.objects.filter(tournament=tournament).order_by('round_number')
    
    return render(request, 'tournament_bracket.html', {
        'tournament': tournament,
        'matches': matches,
    })