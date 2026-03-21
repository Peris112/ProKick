from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    # Links the User (Manager) to exactly one Team
    manager = models.OneToOneField(User, on_delete=models.CASCADE, related_name='team')
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255, default="Kisumu", help_text="Enter home ground or city")   
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Player(models.Model):
    POSITIONS = [
        ('GK', 'Goalkeeper'),
        ('DF', 'Defender'),
        ('MF', 'Midfielder'),
        ('FW', 'Forward'),
    ]
    # Connects the player to a specific team
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player_profile', null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=2, choices=POSITIONS)
    jersey_number = models.PositiveIntegerField()
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.team.name})"

class MatchRequest(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('A', 'Accepted'),
        ('D', 'Declined'),
    ]
    # Two foreign keys to the same table require 'related_name'
    sender = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='sent_challenges')
    receiver = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='received_challenges')
    match_date = models.DateTimeField()
    venue = models.CharField(max_length=255)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} vs {self.receiver} - {self.status}"

class Report(models.Model):
    # Handles bullying or technical complaints
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report: {self.subject} by {self.reporter}"