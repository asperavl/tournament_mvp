from django.shortcuts import render, redirect, get_object_or_404
from .models import Tournament, Team, Match
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from .forms import TeamRegistrationForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

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
def register_team(request, tournament_id):
    # Fetch the tournament based on its ID
    tournament = Tournament.objects.get(id=tournament_id)

    # Check if the tournament is available for registration
    if tournament.status != 'available':
        return redirect('dashboard')  # Redirect if the tournament is not available

    # Check if the tournament has reached its max teams
    if tournament.num_teams_registered >= tournament.max_teams:
        # Display an error message if the tournament is full
        messages.error(request, f"This tournament has already reached the maximum number of {tournament.max_teams} teams.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = TeamRegistrationForm(request.POST)
        if form.is_valid():
            # Save the new team but don't commit yet
            team = form.save(commit=False)
            tournament.users.add(request.user)  # Add user to tournament's users field
            team.tournament = tournament  # Associate the team with the tournament
            team.user = request.user  # Assign the logged-in user to the team
            team.save()

            # Increment the number of teams registered for the tournament
            tournament.num_teams_registered += 1
            tournament.save()

            return redirect('dashboard')  # Redirect to dashboard after successful registration
    else:
        form = TeamRegistrationForm()

    return render(request, 'register_team.html', {'form': form, 'tournament': tournament})


@login_required
def dashboard(request):
    user = request.user
    # Get tournaments the user has registered for
    tournaments = Tournament.objects.filter(users=user)

    # Get all available tournaments
    available_tournaments = Tournament.objects.filter(status='available')

    return render(request, 'dashboard.html', {
        'user': user,
        'tournaments': tournaments,  # Registered tournaments
        'available_tournaments': available_tournaments,  # Available tournaments
    })

@login_required
def view_tournament_bracket(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    
    # Get all matches for this tournament, ordered by round
    matches = Match.objects.filter(tournament=tournament).order_by('round_number')

    return render(request, 'tournament_bracket.html', {
        'tournament': tournament,
        'matches': matches,
    })
