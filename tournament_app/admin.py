from django.contrib import admin
from .models import Tournament, Team, Match
from django.contrib.auth.models import User
from django import forms

from django.contrib import admin
from .models import Tournament

class TournamentAdminForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Always exclude superusers from the users field choices
        self.fields['users'].queryset = User.objects.exclude(is_superuser=True)
        
        # If editing an existing tournament, remove any superusers that might be already assigned
        if self.instance.pk:
            self.initial['users'] = list(self.instance.users.exclude(is_superuser=True).values_list('id', flat=True))

class TournamentAdmin(admin.ModelAdmin):
    form = TournamentAdminForm

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Always ensure no superusers are in the users field
        obj.users.remove(*obj.users.filter(is_superuser=True))


admin.site.register(Tournament, TournamentAdmin)
admin.site.register(Team)
admin.site.register(Match)
