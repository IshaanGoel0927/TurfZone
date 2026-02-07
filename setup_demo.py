import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from turfbooking.models import Turf

def create_demo_data():
    print("Refreshing database...")
    Turf.objects.all().delete() # Clears old data

    demo_turfs = [
        {"name": "Skyline Arena", "location": "Downtown Heights, Level 42", "price": 1200.00, "res": False},
        {"name": "Neon District Turf", "location": "Cyber Hub, Sector 5", "price": 850.50, "res": False},
        {"name": "The Iron Cage", "location": "Westend Mall Rooftop", "price": 600.00, "res": False},
        {"name": "Vortex Sports Complex", "location": "Phoenix Towers, South Wing", "price": 1500.00, "res": True},
        {"name": "Zenith Field", "location": "Aurora Skydeck", "price": 2000.00, "res": False},
        {"name": "Urban Jungle", "location": "Green Park Extension", "price": 950.00, "res": True},
        {"name": "Thunderdome", "location": "Industrial Area, Phase 1", "price": 500.00, "res": False},
        {"name": "Cloud 9 Pitch", "location": "Sky Garden Residencies", "price": 0.00, "res": True},
        {"name": "Matrix Field", "location": "Tech Park, Building C", "price": 1100.00, "res": False},
        {"name": "The Colosseum", "location": "Grand Mall Terrace", "price": 1800.00, "res": False},
    ]

    for data in demo_turfs:
        Turf.objects.create(
            name=data["name"],
            location=data["location"],
            price_per_hour=data["price"],
            is_residential=data["res"]
        )
        print(f" - Created: {data['name']}")

    print("\nDATABASE UPDATED: 10 Turfs Live.")

if __name__ == "__main__":
    create_demo_data()