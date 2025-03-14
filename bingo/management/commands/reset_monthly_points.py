#!/usr/bin/env python3
# 
from django.core.management.base import BaseCommand
from django.utils.timezone import now
from bingo.models import Leaderboard

class Command(BaseCommand):
    help = "Resets the monthly points of all players at the start of a new month."

    def handle(self, *args, **kwargs):
        today = now().date()
        if today.day == 1:  # Only reset on the 1st of the month
            players = Leaderboard.objects.all()
            for player in players:
                player.reset_monthly_points()
            self.stdout.write(self.style.SUCCESS("Successfully reset monthly leaderboard."))
        else:
            self.stdout.write(self.style.WARNING("Today is not the 1st day of the month. Skipping reset."))
