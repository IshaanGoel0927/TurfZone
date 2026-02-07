from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q 
from django.core.exceptions import ValidationError 
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
import json
import datetime

from .models import Turf, Booking
from .forms import SignUpForm, BookingForm, ContactForm

# --- PUBLIC PAGES ---

def home(request):
    # Show top 3 turfs on homepage
    turfs = Turf.objects.all()[:3]
    return render(request, 'home.html', {'turfs': turfs})

def explore(request):
    # Search functionality
    query = request.GET.get('q')
    if query:
        turfs = Turf.objects.filter(
            Q(name__icontains=query) | Q(location__icontains=query)
        )
    else:
        turfs = Turf.objects.all()
    return render(request, 'explore.html', {'turfs': turfs, 'query': query})

def about(request):
    return render(request, 'about.html')

def privacy(request):
    return render(request, 'privacy.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Message Received! We will deploy a support agent shortly.")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

# --- AUTHENTICATION ---

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Log them in immediately
            messages.success(request, "Account created! Welcome to the arena.")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

# --- USER DASHBOARD ---

@login_required
def dashboard(request):
    # STRICT PRIVACY: Only show bookings for the logged-in user
    bookings = Booking.objects.filter(user=request.user).order_by('-date', '-start_time')
    return render(request, 'dashboard.html', {'bookings': bookings})

@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')
    return render(request, 'profile.html')

# --- BOOKING ENGINE (The Core Logic) ---

@login_required
def book_turf(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)
    
    # 1. SMART FETCH: Get all busy slots (Confirmed OR Pending)
    # This prevents race conditions where two people book the same slot
    busy_slots = Booking.objects.filter(
        turf=turf, 
        date__gte=datetime.date.today(),
        status__in=['CONFIRMED', 'PENDING']  # Block pending slots too!
    ).values('date', 'start_time', 'end_time')

    # 2. Convert to JSON for the Frontend JavaScript
    busy_data = json.dumps(list(busy_slots), cls=DjangoJSONEncoder)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
                # Create instance but don't save to DB yet
                booking = form.save(commit=False)
                booking.user = request.user
                booking.turf = turf
                booking.status = 'PENDING'
                
                # Check for conflicts (Models.py logic runs here)
                booking.clean() 
                
                # If clean() passes, save and go to payment
                booking.save()
                return redirect('payment', booking_id=booking.id)
            
            except ValidationError as e:
                # If model finds a conflict, show error on form
                form.add_error(None, e)
            except Exception as e:
                # Catch unexpected database errors
                messages.error(request, f"System Error: {e}")
    else:
        form = BookingForm()
    
    return render(request, 'booking.html', {'form': form, 'turf': turf, 'busy_data': busy_data})

# --- PAYMENT & CANCELLATION ---

@login_required
def payment(request, booking_id):
    # Securely fetch booking (ensure it belongs to user)
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # If already paid, don't show payment page again
    if booking.status == 'CONFIRMED':
        messages.info(request, "Booking already paid.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        booking.status = 'CONFIRMED'
        booking.save()
        messages.success(request, "Payment Successful! Game On.")
        return redirect('dashboard')
        
    return render(request, 'payment.html', {'booking': booking})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Idempotency: Don't cancel twice
    if booking.status == 'CANCELLED':
        messages.info(request, "This booking is already cancelled.")
        return redirect('dashboard')

    # 1. Calculate Refund based on logic
    refund_amount, reason = booking.calculate_refund()
    
    # 2. Update Booking
    booking.status = 'CANCELLED'
    booking.refund_amount = refund_amount
    booking.save()
    
    # 3. Logic-Specific Messages
    if refund_amount > 0:
        messages.success(request, f"Booking Cancelled. Refund of ₹{refund_amount} initiated. Reason: {reason}")
    else:
        messages.warning(request, f"Booking Cancelled. No refund applicable. Reason: {reason}")
    
    return redirect('dashboard')