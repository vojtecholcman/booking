import io
import os
from django.core.files.base import ContentFile
from django.db import models


TIME_SLOTS = [
    "18:00", "19:00", "20:00", "21:00", "22:00", "23:00",
    "00:00", "01:00", "02:00", "03:00", "04:00", "05:00",
]


class Room(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    max_guests = models.PositiveIntegerField()
    photo = models.ImageField(upload_to='rooms/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_hourly = models.BooleanField(default=False, verbose_name='Hodinové rezervace')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.photo:
            from PIL import Image
            img = Image.open(self.photo)
            if img.format == 'HEIF':
                img = img.convert('RGB')
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=90)
                name = os.path.splitext(self.photo.name)[0] + '.jpg'
                self.photo = ContentFile(buffer.getvalue(), name=os.path.basename(name))
        super().save(*args, **kwargs)

    @property
    def current_guest_count(self):
        return sum(r.guests.count() for r in self.reservations.all())

    @property
    def is_full(self):
        if self.is_hourly:
            # plný = každý slot je obsazený na max
            guests_by_slot = {}
            for r in self.reservations.all():
                if r.time_slot:
                    guests_by_slot[r.time_slot] = guests_by_slot.get(r.time_slot, 0) + r.guests.count()
            return all(guests_by_slot.get(t, 0) >= self.max_guests for t in TIME_SLOTS)
        return self.current_guest_count >= self.max_guests

    @property
    def remaining_capacity(self):
        return max(0, self.max_guests - self.current_guest_count)


class Reservation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reservations')
    created_at = models.DateTimeField(auto_now_add=True)
    time_slot = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        names = ', '.join(g.name for g in self.guests.all())
        return f'{self.room.name}: {names}'


class Guest(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='guests')
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
