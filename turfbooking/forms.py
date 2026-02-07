from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Booking, ContactMessage
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

# 1. Sign Up Form
class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full bg-gray-900 border border-gray-700 rounded-xl text-white px-4 py-3 focus:outline-none focus:border-green-500 transition'

# 2. Contact Form
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Name', 'class': 'w-full bg-black border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-green-500'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'w-full bg-black border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-green-500'}),
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'How can we help?', 'class': 'w-full bg-black border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-green-500'}),
        }

# 3. Booking Form (Time-Aware + Min Duration)
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full bg-gray-900 border border-gray-700 rounded-xl text-white px-4 py-3 focus:outline-none focus:border-green-500 transition'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full bg-gray-900 border border-gray-700 rounded-xl text-white px-4 py-3 focus:outline-none focus:border-green-500 transition'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full bg-gray-900 border border-gray-700 rounded-xl text-white px-4 py-3 focus:outline-none focus:border-green-500 transition'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        booking_date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        # 1. Basic Checks
        if not (booking_date and start_time and end_time):
            return cleaned_data

        now = timezone.now()
        today = now.date()

        # 2. Past Date Check
        if booking_date < today:
            raise ValidationError("You cannot travel back in time! Please select a future date.")

        # 3. Past Time Check (The "User cannot book passed time" fix)
        if booking_date == today:
            current_time = now.time()
            if start_time < current_time:
                raise ValidationError("This time slot has already passed for today.")

        # 4. End Time Check
        if start_time >= end_time:
            raise ValidationError("End time must be after start time.")
            
        # 5. Minimum Duration Check (The "Minimum Time" fix)
        # Create dummy dates to compare duration
        dummy_date = datetime.today().date()
        t1 = datetime.combine(dummy_date, start_time)
        t2 = datetime.combine(dummy_date, end_time)
        
        duration_minutes = (t2 - t1).total_seconds() / 60
        
        if duration_minutes < 60:
            raise ValidationError("Minimum booking duration is 1 hour (60 minutes).")

        return cleaned_data