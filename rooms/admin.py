from django.contrib import admin
from django.utils.html import format_html

from .models import Guest, Reservation, Room, RoomPhoto


class GuestInline(admin.TabularInline):
    model = Guest
    extra = 0


class RoomPhotoInline(admin.TabularInline):
    model = RoomPhoto
    extra = 3
    fields = ('photo', 'order')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_guests', 'guest_count', 'remaining', 'is_active', 'photo_preview')
    list_editable = ('is_active',)
    fields = ('name', 'description', 'max_guests', 'is_active', 'is_hourly')
    inlines = [RoomPhotoInline]

    @admin.display(description='Hosté')
    def guest_count(self, obj):
        return obj.current_guest_count

    @admin.display(description='Zbývá')
    def remaining(self, obj):
        return obj.remaining_capacity

    @admin.display(description='Foto')
    def photo_preview(self, obj):
        first = obj.photos.first()
        if first:
            return format_html('<img src="{}" style="height:40px;border-radius:4px">', first.photo.url)
        return '—'


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('room', 'time_slot', 'guest_names', 'created_at')
    list_filter = ('room',)
    inlines = [GuestInline]

    @admin.display(description='Hosté')
    def guest_names(self, obj):
        return ', '.join(g.name for g in obj.guests.all()) or '—'
