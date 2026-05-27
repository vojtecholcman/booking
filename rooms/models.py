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

    @property
    def current_guest_count(self):
        return sum(r.guests.count() for r in self.reservations.all())

    @property
    def is_full(self):
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
