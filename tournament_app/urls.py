from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('register-team/<slug:tournament_slug>/', views.register_team, name='register_team'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tournament/<slug:tournament_slug>/bracket/', views.view_tournament_bracket, name='view_bracket'),
]
