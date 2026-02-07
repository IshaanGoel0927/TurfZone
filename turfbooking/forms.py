from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Booking
from django.core.exceptions import ValidationError

# 1. Sign Up Form (Fixes the invisible text issue)
class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        # This loop adds the dark-mode styling to every field automatically
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full bg-gray-700 border border-gray-600 rounded text-white px-3 py-2 focus:outline-none focus:border-green-500'
            field.help_text = None # Optional: Removes the messy "password requirements" text if you want a cleaner look

# 2. Booking Form
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full bg-gray-700 border border-gray-600 rounded text-white px-3 py-2 focus:outline-none focus:border-green-500'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full bg-gray-700 border border-gray-600 rounded text-white px-3 py-2 focus:outline-none focus:border-green-500'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full bg-gray-700 border border-gray-600 rounded text-white px-3 py-2 focus:outline-none focus:border-green-500'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")

        if start and end:
            if start >= end:
                raise ValidationError("End time must be after start time.")
        return cleaned_data