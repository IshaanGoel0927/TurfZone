from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q # For search logic
from .models import Turf, Booking
from .forms import SignUpForm, BookingForm

def home(request):
    # Show only top 3 "Featured" turfs on home to keep it clean
    turfs = Turf.objects.all()[:3]
    return render(request, 'home.html', {'turfs': turfs})

def explore(request):
    query = request.GET.get('q')
    if query:
        # Search by Name OR Location
        turfs = Turf.objects.filter(
            Q(name__icontains=query) | Q(location__icontains=query)
        )
    else:
        turfs = Turf.objects.all()
    
    return render(request, 'explore.html', {'turfs': turfs, 'query': query})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created! Welcome to the arena.")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def dashboard(request):
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

@login_required
def book_turf(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
                booking = form.save(commit=False)
                booking.user = request.user
                booking.turf = turf
                booking.status = 'PENDING'
                booking.clean() 
                booking.save()
                return redirect('payment', booking_id=booking.id)
            except Exception as e:
                messages.error(request, f"Error: {e}")
    else:
        form = BookingForm()
    return render(request, 'booking.html', {'form': form, 'turf': turf})

@login_required
def payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
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
    if booking.status != 'CANCELLED':
        booking.status = 'CANCELLED'
        booking.save()
        messages.warning(request, "Booking Cancelled.")
    return redirect('dashboard')

# Static Pages
def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')
# ... existing imports ...

# ADD THIS FUNCTION AT THE END
def privacy(request):
    return render(request, 'privacy.html')