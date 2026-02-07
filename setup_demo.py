import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from turfbooking.models import Turf
from django.core.files import File

def create_turfs():
    # Clear existing data to avoid duplicates
    Turf.objects.all().delete()
    print("Cleaned old data...")

    turfs = [
        {
            "name": "The Arena",
            "location": "Sector 29, Gurgaon",
            "price": 1200.00,
            "is_residential": False
        },
        {
            "name": "Hat-Trick Sports",
            "location": "Vasant Kunj, Delhi",
            "price": 1500.00,
            "is_residential": True
        },
        {
            "name": "Skyline Rooftop",
            "location": "Bandra West, Mumbai",
            "price": 2500.00,
            "is_residential": False
        },
        {
            "name": "Dribble Down",
            "location": "Koramangala, Bangalore",
            "price": 1800.00,
            "is_residential": True
        },
        {
            "name": "Goalazo Pitch",
            "location": "Salt Lake, Kolkata",
            "price": 900.00,
            "is_residential": False
        },
        {
            "name": "Urban Kicks",
            "location": "Jubilee Hills, Hyderabad",
            "price": 2200.00,
            "is_residential": False
        }
    ]

    for data in turfs:
        t = Turf.objects.create(
            name=data["name"],
            location=data["location"],
            price_per_hour=data["price"],
            is_residential=data["is_residential"]
        )
        print(f"Created: {t.name}")

    print("✅ Database populated successfully!")

if __name__ == '__main__':
    create_turfs()