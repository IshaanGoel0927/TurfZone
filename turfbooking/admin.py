from django.contrib import admin
from django.utils.html import mark_safe
from .models import Turf, Booking

# 1. Customize the Turf Admin
class TurfAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'price_per_hour', 'is_residential', 'image_preview')
    list_filter = ('is_residential', 'location') # Sidebar filters
    search_fields = ('name', 'location') # Search bar at the top
    list_editable = ('price_per_hour', 'is_residential') # Edit price directly in the list
    
    # Function to show image thumbnail in admin
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="width: 50px; height:50px; object-fit:cover; border-radius:5px;" />')
        return "No Image"
    image_preview.short_description = 'Image'

# 2. Customize the Booking Admin
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'turf', 'date', 'start_time', 'end_time', 'status_color')
    list_filter = ('date', 'turf')
    search_fields = ('user__username', 'turf__name')
    date_hierarchy = 'date' # visual date drill-down navigation
    
    def status_color(self, obj):
        return mark_safe('<span style="color:green; font-weight:bold;">Confirmed</span>')
    status_color.short_description = 'Status'

admin.site.register(Turf, TurfAdmin)
admin.site.register(Booking, BookingAdmin)