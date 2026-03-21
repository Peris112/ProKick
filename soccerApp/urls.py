
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # General Pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Team & Player Directory
    path('teams/', views.team_list, name='team_list'),
    path('schedule/', views.match_schedule, name='schedule'),
    
    # Management & Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register-player/', views.register_player, name='register_player'),
    path('request/<int:request_id>/<str:action>/', views.handle_request, name='handle_request'),
    
    # Authentication
    path('signup/', views.manager_signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='soccerApp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    path('conduct/', views.conduct, name='conduct'),

    path('reset-player/<int:player_id>/', views.reset_player_password, name='reset_player_password'),

]
