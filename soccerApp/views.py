from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .models import Team, MatchRequest, Player, Report
from django.contrib.auth.models import User
from django.core.mail import send_mail 

# ==========================================
# 1. Home, About & Contact
# ==========================================
def home(request):
    return render(request, 'soccerApp/home.html')

def about(request):
    return render(request, 'soccerApp/about.html')

def conduct(request):
    return render(request, 'soccerApp/conduct.html')

def contact(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        reporter = request.user if request.user.is_authenticated else "Anonymous"
        
        # 1. Save to Database (Existing Logic)
        Report.objects.create(
            reporter=request.user if request.user.is_authenticated else None, 
            subject=subject, 
            message=message
        )

        # 2. Send Email Notification
        full_email_message = f"New Report from {reporter}:\n\nSubject: {subject}\n\nMessage: {message}"
        
        try:
            send_mail(
                subject=f"URGENT: ProKick Hub Report - {subject}",
                message=full_email_message,
                from_email='your-official-email@gmail.com',
                recipient_list=['admin-leader-email@gmail.com'], # Where you want to receive it
                fail_silently=False,
            )
        except Exception as e:
            # If email fails (no internet, etc), the DB record is still safe!
            print(f"Email failed: {e}")

        messages.success(request, "Your report has been submitted to the leaders.")
        return redirect('home')
        
    return render(request, 'soccerApp/contact.html')

# ==========================================
# 2. Team & Schedule (Public)
# ==========================================
def team_list(request):
    teams = Team.objects.all()
    return render(request, 'soccerApp/team_list.html', {'teams': teams})

def match_schedule(request):
    matches = MatchRequest.objects.exclude(status='D').order_by('match_date')
    return render(request, 'soccerApp/match_schedule.html', {'matches': matches})

# ==========================================
# 3. Manager Signup Logic (Updated with Location)
# ==========================================
def manager_signup(request):
    if request.method == 'POST':
        manager_name = request.POST.get('manager_name')
        team_name = request.POST.get('team_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        # Capture the location from the new form field
        location = request.POST.get('location')

        # Create the User account
       # Clean the name to remove spaces for the username
        clean_username = manager_name.replace(" ", "_").lower()

        user = User.objects.create_user(
            username=clean_username, 
            email=email, 
            password=password, 
            first_name=manager_name
        )
        
        # Create the Team profile linked to this User with the actual location
        Team.objects.create(
            manager=user, 
            name=team_name, 
            location=location
        )
        
        login(request, user)
        messages.success(request, f"Welcome Coach {manager_name}! Your team in {location} is now registered.")
        return redirect('dashboard')
        
    return render(request, 'soccerApp/signup.html')

# ==========================================
# 4. Redirect Logic
# ==========================================
@login_required
def login_success(request):
    if hasattr(request.user, 'team'):
        return redirect('dashboard')
    return redirect('home')

# ==========================================
# 5. Manager Dashboard & Player Registration
# ==========================================
@login_required
def dashboard(request):
    if not hasattr(request.user, 'team'):
        return redirect('home')
    
    team = request.user.team
    
    # Matches YOU received that are still Pending
    received_requests = MatchRequest.objects.filter(receiver=team, status='P')
    
    # Matches YOU sent (All of them, so you can see if they are Pending, Accepted, or Declined)
    sent_requests = MatchRequest.objects.filter(sender=team).order_by('-created_at')
    
    # NEW: Specifically grab challenges you sent that were DECLINED
    declined_notifications = MatchRequest.objects.filter(sender=team, status='D')

    players = Player.objects.filter(team=team)
    
    return render(request, 'soccerApp/dashboard.html', {
        'team': team,
        'received_requests': received_requests,
        'sent_requests': sent_requests,
        'declined_notifications': declined_notifications, # Pass this to HTML
        'players': players,
    })

@login_required
def register_player(request):
    if not hasattr(request.user, 'team'):
        return redirect('home')

    if request.method == 'POST':
        name = request.POST.get('name')
        jersey = request.POST.get('number')
        position = request.POST.get('position')
        
        # Unique ID logic (e.g., John_Doe_7)
        username = f"{name.replace(' ', '_')}_{jersey}"
        team_password = "st_2026" 

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username, 
                password=team_password
            )
            
            Player.objects.create(
                user=user,
                team=request.user.team,
                name=name,
                position=position,
                jersey_number=jersey
            )
            messages.success(request, f"Player added! ID: {username} | Password: {team_password}")
        else:
            messages.error(request, "A player with this ID already exists.")
            
        return redirect('dashboard')

    return render(request, 'soccerApp/register.html')

# ==========================================
# 6. Actions & Password Management
# ==========================================
@login_required
def handle_request(request, request_id, action):
    match_req = get_object_or_404(MatchRequest, id=request_id)
    
    if match_req.receiver == request.user.team:
        if action == 'accept':
            match_req.status = 'A'
            messages.success(request, "Match Accepted!")
        elif action == 'decline':
            match_req.status = 'D'
            messages.warning(request, "Match Declined.")
        match_req.save()
        
    return redirect('dashboard')

@login_required
def reset_player_password(request, player_id):
    player = get_object_or_404(Player, id=player_id)
    
    # Ensure only the player's own manager can reset their password
    if request.user.team == player.team:
        user_to_reset = player.user
        common_pass = "st_2026" 
        
        # Use set_password to ensure the password is hashed correctly in SQLite
        user_to_reset.set_password(common_pass)
        user_to_reset.save()
        
        messages.success(request, f"Password for {player.name} reset to: {common_pass}")
    else:
        messages.error(request, "Unauthorized access.")
        
    return redirect('dashboard')


@login_required
def send_challenge(request, receiver_id):
    # 1. Get the team you want to challenge
    receiver_team = get_object_or_404(Team, id=receiver_id)
    sender_team = request.user.team # Your team

    # 2. Prevent challenging yourself
    if sender_team == receiver_team:
        messages.error(request, "You cannot challenge your own team!")
        return redirect('team_list')

    if request.method == 'POST':
        match_date = request.POST.get('match_date')
        venue = request.POST.get('venue')

        # 3. Create the MatchRequest in the DB
        MatchRequest.objects.create(
            sender=sender_team,
            receiver=receiver_team,
            match_date=match_date,
            venue=venue,
            status='P' # Defaults to Pending
        )
        messages.success(request, f"Challenge sent to {receiver_team.name}!")
        return redirect('dashboard')

    return render(request, 'soccerApp/send_challenge.html', {'receiver': receiver_team})