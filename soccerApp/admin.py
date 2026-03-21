from django.contrib import admin
from .models import Team, Player, MatchRequest, Report

# 1. Customizing the Team View
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    # What columns to show in the list view
    list_display = ('name', 'manager', 'location', 'created_at')
    # Add a search bar for team names and locations
    search_fields = ('name', 'location')
    # Add a sidebar filter for dates
    list_filter = ('created_at', 'location')
    # Make the manager link clickable
    raw_id_fields = ('manager',)

# 2. Customizing the Player View
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'team', 'position', 'jersey_number', 'is_active')
    list_filter = ('position', 'team', 'is_active')
    search_fields = ('name',)
    # Allows you to edit 'is_active' directly from the list view
    list_editable = ('is_active',)

# 3. Customizing the Match Request View (The League Overview)
@admin.register(MatchRequest)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'match_date', 'status', 'venue')
    list_filter = ('status', 'match_date')
    # Group by status to see 'Pending' matches easily
    ordering = ('-match_date',)

# 4. Customizing the Report View (Safety & Conduct)
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('subject', 'reporter', 'timestamp', 'is_resolved')
    list_filter = ('is_resolved', 'timestamp')
    search_fields = ('subject', 'message')
    # Color-code or highlight resolved vs unresolved in the future
    list_editable = ('is_resolved',)