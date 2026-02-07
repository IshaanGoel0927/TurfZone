from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Turf(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='turfs/', blank=True, null=True) # New Image Field
    is_residential = models.BooleanField(default=False)
    price_per_hour = models.DecimalField(max_digits=6, decimal_places=2)
    
    def __str__(self):
        return self.name

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # The Logic: Check if any booking overlaps with the requested time
        overlapping_bookings = Booking.objects.filter(
            turf=self.turf,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(id=self.id) # Exclude self if editing

        if overlapping_bookings.exists():
            raise ValidationError("This time slot is already booked.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.turf.name}"