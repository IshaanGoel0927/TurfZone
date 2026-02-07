from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('explore/', views.explore, name='explore'), # New Search Page
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'), # New Profile Settings
    path('about/', views.about, name='about'),       # New Static Page
    path('contact/', views.contact, name='contact'), # New Static Page
    path('privacy/', views.privacy, name='privacy'),
    
    # Auth
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # Booking
    path('book/<int:turf_id>/', views.book_turf, name='book_turf'),
    path('payment/<int:booking_id>/', views.payment, name='payment'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
]