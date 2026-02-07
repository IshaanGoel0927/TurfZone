from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta, datetime, date

# 1. TURF MODEL
class Turf(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='turfs/', blank=True, null=True)
    is_residential = models.BooleanField(default=False)
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2)
    
    def __str__(self):
        return self.name

# 2. CONTACT MESSAGE MODEL
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"

# 3. BOOKING MODEL (The Core Logic)
class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Financials
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    refund_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00) # New Field
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    
    created_at = models.DateTimeField(auto_now_add=True)

    # --- 1. CLASH DETECTION ---
    def clean(self):
        # Basic Validation
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")
        
        try:
            current_turf = self.turf
        except Exception:
            return

        # Conflict Check (Blocks Confirmed & Pending)
        overlapping_bookings = Booking.objects.filter(
            turf=current_turf,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
            status__in=['CONFIRMED', 'PENDING']
        ).exclude(id=self.id)

        if overlapping_bookings.exists():
            raise ValidationError("Clash Detected: This slot is currently locked by another user.")

    # --- 2. SMART REFUND CALCULATOR ---
    def calculate_refund(self):
        """
        Returns a tuple: (Refund Amount, Message Percentage)
        """
        now = timezone.now()
        
        # Combine date and time to get the Game Start Timestamp
        game_start = datetime.combine(self.date, self.start_time)
        # Make it timezone aware (crucial for accurate math)
        game_start = timezone.make_aware(game_start)

        # 1. Past Game? (No Refund)
        if game_start < now:
            return 0.00, "0% (Game already started)"

        # 2. The "Oops" Rule (Grace Period)
        # If booked less than 1 hour ago -> 100% Refund
        time_since_booking = now - self.created_at
        if time_since_booking < timedelta(hours=1):
            return self.total_price, "100% (Instant Cancellation Grace Period)"

        # 3. Time until game starts
        time_until_game = game_start - now

        # 4. The "Early Bird" Rule (> 24 hours before game)
        if time_until_game > timedelta(hours=24):
            return self.total_price, "100% (Early Cancellation)"

        # 5. The "Standard" Rule (Between 4 and 24 hours)
        elif time_until_game > timedelta(hours=4):
            half_refund = self.total_price / 2
            return half_refund, "50% (Standard Cancellation Fee Applied)"

        # 6. The "No-Show" Rule (< 4 hours)
        else:
            return 0.00, "0% (Last Minute Cancellation)"

    def save(self, *args, **kwargs):
        # Auto-calculate Price on Save
        if self.start_time and self.end_time and self.turf:
            t1 = datetime.combine(date.today(), self.start_time)
            t2 = datetime.combine(date.today(), self.end_time)
            duration_hours = (t2 - t1).seconds / 3600
            self.total_price = round(float(self.turf.price_per_hour) * duration_hours, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.turf.name} ({self.status})"