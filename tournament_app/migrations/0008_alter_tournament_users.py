# Generated by Django 5.1.7 on 2025-04-01 00:04

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament_app', '0007_remove_tournament_max_teams'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='users',
            field=models.ManyToManyField(blank=True, null=True, related_name='registered_tournaments', to=settings.AUTH_USER_MODEL),
        ),
    ]
