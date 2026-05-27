import io
import os
from django.core.files.base import ContentFile
from django.db import models


TIME_SLOTS = [
    "18:00", "19:00", "20:00", "21:00", "22:00", "23:00",
    "00:00", "01:00", "02:00", "03:00", "04:00", "05:00",
]


def _convert_heic(field):
    """Convert HEIC photo to JPEG in-place after the model is already saved."""
    try:
        from PIL import Image
        img = Image.open(field.path)
        if img.format != 'HEIF':
            return None
        img = img.convert('RGB')
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=90)
        old_path = field.path
        new_name = os.path.splitext(os.path.basename(field.name))[0] + '.jpg'
        field.save(new_name, ContentFile(buf.getvalue()), save=False)
        if old_path != field.path and os.path.exists(old_path):
            os.remove(old_path)
        return field.name
    except Exception:
        return None


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
        super().save(*args, **kwargs)
        if self.photo and 'update_fields' not in kwargs:
            new_name = _convert_heic(self.photo)
            if new_name:
                type(self).objects.filter(pk=self.pk).update(photo=new_name)

    @property
    def current_guest_count(self):
        return sum(r.guests.count() for r in self.reservations.all())

    @property
    def is_full(self):
        if self.is_hourly:
            guests_by_slot = {}
            for r in self.reservations.all():
                if r.time_slot:
                    guests_by_slot[r.time_slot] = guests_by_slot.get(r.time_slot, 0) + r.guests.count()
            return all(guests_by_slot.get(t, 0) >= self.max_guests for t in TIME_SLOTS)
        return self.current_guest_count >= self.max_guests

    @property
    def remaining_capacity(self):
        return max(0, self.max_guests - self.current_guest_count)


class RoomPhoto(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='rooms/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'pk']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.photo and 'update_fields' not in kwargs:
            new_name = _convert_heic(self.photo)
            if new_name:
                type(self).objects.filter(pk=self.pk).update(photo=new_name)


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
