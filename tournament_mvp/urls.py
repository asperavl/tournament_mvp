from django.contrib import admin
from django.urls import path, include  # Import include

urlpatterns = [
    path('admin/', admin.site.urls),          # Admin page
    path('', include('tournament_app.urls')),  # Include URLs from your app
]
