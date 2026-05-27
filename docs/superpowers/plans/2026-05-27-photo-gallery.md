# Photo Gallery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Bootstrap 5 carousel on the room detail page that shows multiple photos per room.

**Architecture:** New `RoomPhoto` model holds additional photos (FK to Room, order integer). The HEIC→JPEG conversion logic is extracted to a shared helper used by both `Room` and `RoomPhoto`. The view builds a flat `photos` URL list passed to the template; the template renders a plain `<img>` for 1 photo or a Bootstrap 5 carousel for 2+.

**Tech Stack:** Django 5, Bootstrap 5 (already loaded in base.html), Pillow + pillow-heif

---

## File Map

| File | Action |
|------|--------|
| `rooms/models.py` | Extract `_convert_heic` helper; add `RoomPhoto` model |
| `rooms/migrations/0003_roomphoto.py` | Auto-generated via `makemigrations` |
| `rooms/admin.py` | Add `RoomPhotoInline`; wire into `RoomAdmin` |
| `rooms/views.py` | Add `_room_photos` helper; pass `photos` to `room_detail` context |
| `rooms/templates/rooms/room_detail.html` | Replace single `<img>` with carousel block |
| `rooms/tests.py` | Tests for `_room_photos` helper and carousel rendering |

---

### Task 1: Extract HEIC helper and add RoomPhoto model

**Files:**
- Modify: `rooms/models.py`

- [ ] **Step 1: Replace models.py with updated version**

Full new content of `rooms/models.py`:

```python
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
```

- [ ] **Step 2: Verify Python syntax**

```bash
python -c "import rooms.models"
```
Expected: no output (no errors)

---

### Task 2: Create and run migration

**Files:**
- Create: `rooms/migrations/0003_roomphoto.py` (auto-generated)

- [ ] **Step 1: Generate migration**

```bash
python manage.py makemigrations rooms --name roomphoto
```
Expected output:
```
Migrations for 'rooms':
  rooms/migrations/0003_roomphoto.py
    - Create model RoomPhoto
```

- [ ] **Step 2: Apply migration**

```bash
python manage.py migrate
```
Expected: `Applying rooms.0003_roomphoto... OK`

- [ ] **Step 3: Commit**

```bash
git add rooms/models.py rooms/migrations/0003_roomphoto.py
git commit -m "feat: add RoomPhoto model with HEIC conversion"
```

---

### Task 3: Add RoomPhotoInline to admin

**Files:**
- Modify: `rooms/admin.py`

- [ ] **Step 1: Update admin.py**

Full new content of `rooms/admin.py`:

```python
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
    fields = ('name', 'description', 'max_guests', 'photo', 'is_active', 'is_hourly')
    inlines = [RoomPhotoInline]

    @admin.display(description='Hosté')
    def guest_count(self, obj):
        return obj.current_guest_count

    @admin.display(description='Zbývá')
    def remaining(self, obj):
        return obj.remaining_capacity

    @admin.display(description='Foto')
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="height:40px;border-radius:4px">', obj.photo.url)
        return '—'


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('room', 'time_slot', 'guest_names', 'created_at')
    list_filter = ('room',)
    inlines = [GuestInline]

    @admin.display(description='Hosté')
    def guest_names(self, obj):
        return ', '.join(g.name for g in obj.guests.all()) or '—'
```

- [ ] **Step 2: Commit**

```bash
git add rooms/admin.py
git commit -m "feat: add RoomPhoto inline in admin"
```

---

### Task 4: Update view to pass photos list

**Files:**
- Modify: `rooms/views.py`

- [ ] **Step 1: Add `_room_photos` helper and update `room_detail`**

Add the helper after the imports and update the non-hourly render call.

Full new content of `rooms/views.py`:

```python
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render

from .models import TIME_SLOTS, Guest, Reservation, Room


def _room_photos(room):
    photos = []
    if room.photo:
        photos.append(room.photo.url)
    for rp in room.photos.all():
        photos.append(rp.photo.url)
    return photos


def login_view(request):
    error = None
    if request.method == 'POST':
        if request.POST.get('password') == settings.SITE_PASSWORD:
            request.session['site_authenticated'] = True
            return redirect(request.GET.get('next', '/'))
        error = 'Špatné heslo, zkus to znovu.'
    return render(request, 'rooms/login.html', {'error': error})


def logout_view(request):
    request.session.flush()
    return redirect('/login/')


def room_list(request):
    rooms = Room.objects.filter(is_active=True).prefetch_related('reservations__guests')
    return render(request, 'rooms/room_list.html', {'rooms': rooms})


def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk, is_active=True)
    error = None

    if room.is_hourly:
        reservations = room.reservations.prefetch_related('guests').filter(time_slot__isnull=False)
        guests_by_slot = {}
        for r in reservations:
            guests_by_slot.setdefault(r.time_slot, []).extend(r.guests.all())

        slots = []
        for t in TIME_SLOTS:
            slot_guests = guests_by_slot.get(t, [])
            count = len(slot_guests)
            slots.append({
                'time': t,
                'guests': slot_guests,
                'count': count,
                'remaining': max(0, room.max_guests - count),
                'full': count >= room.max_guests,
            })

        if request.method == 'POST':
            slot = request.POST.get('time_slot')
            names = [v.strip() for v in request.POST.getlist('guest_name') if v.strip()]
            slot_data = next((s for s in slots if s['time'] == slot), None)
            if not slot_data:
                error = 'Neplatný časový slot.'
            elif slot_data['full']:
                error = 'Tento slot je plně obsazen.'
            elif not names:
                error = 'Zadej aspoň jedno jméno.'
            elif len(names) > slot_data['remaining']:
                error = f'Do tohoto slotu se vejde jen {slot_data["remaining"]} dalších lidí.'
            else:
                reservation = Reservation.objects.create(room=room, time_slot=slot)
                for name in names:
                    Guest.objects.create(reservation=reservation, name=name)
                return redirect('confirm', pk=reservation.pk)

        return render(request, 'rooms/room_detail_hourly.html', {
            'room': room,
            'slots': slots,
            'error': error,
        })

    if request.method == 'POST':
        if room.is_full:
            return redirect('room_detail', pk=pk)
        names = [v.strip() for v in request.POST.getlist('guest_name') if v.strip()]
        if not names:
            error = 'Zadej aspoň jedno jméno.'
        else:
            remaining = room.remaining_capacity
            if len(names) > remaining:
                error = f'Zbývá jen {remaining} míst.'
            else:
                reservation = Reservation.objects.create(room=room)
                for name in names:
                    Guest.objects.create(reservation=reservation, name=name)
                return redirect('confirm', pk=reservation.pk)

    guests = Guest.objects.filter(reservation__room=room).select_related('reservation')
    return render(request, 'rooms/room_detail.html', {
        'room': room,
        'guests': guests,
        'error': error,
        'photos': _room_photos(room),
    })


def confirm(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    return render(request, 'rooms/confirm.html', {'reservation': reservation})
```

- [ ] **Step 2: Commit**

```bash
git add rooms/views.py
git commit -m "feat: pass photos list to room_detail context"
```

---

### Task 5: Update room_detail template with carousel

**Files:**
- Modify: `rooms/templates/rooms/room_detail.html`

- [ ] **Step 1: Replace the photo block**

In `rooms/templates/rooms/room_detail.html`, replace lines 18–22:

```html
    {% if room.photo %}
      <img class="room-photo mb-3" src="{{ room.photo.url }}" alt="{{ room.name }}">
    {% else %}
      <div class="room-photo-placeholder mb-3">🛏️</div>
    {% endif %}
```

With:

```html
    {% if photos %}
      {% if photos|length == 1 %}
        <img class="room-photo mb-3" src="{{ photos.0 }}" alt="{{ room.name }}">
      {% else %}
        <div id="roomCarousel" class="carousel slide mb-3" data-bs-ride="false">
          <div class="carousel-indicators">
            {% for photo in photos %}
              <button type="button" data-bs-target="#roomCarousel"
                data-bs-slide-to="{{ forloop.counter0 }}"
                {% if forloop.first %}class="active" aria-current="true"{% endif %}
                aria-label="Foto {{ forloop.counter }}"></button>
            {% endfor %}
          </div>
          <div class="carousel-inner">
            {% for photo in photos %}
              <div class="carousel-item {% if forloop.first %}active{% endif %}">
                <img class="d-block w-100 room-photo" src="{{ photo }}" alt="{{ room.name }} – foto {{ forloop.counter }}">
              </div>
            {% endfor %}
          </div>
          <button class="carousel-control-prev" type="button" data-bs-target="#roomCarousel" data-bs-slide="prev">
            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Předchozí</span>
          </button>
          <button class="carousel-control-next" type="button" data-bs-target="#roomCarousel" data-bs-slide="next">
            <span class="carousel-control-next-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Další</span>
          </button>
        </div>
      {% endif %}
    {% else %}
      <div class="room-photo-placeholder mb-3">🛏️</div>
    {% endif %}
```

- [ ] **Step 2: Commit**

```bash
git add rooms/templates/rooms/room_detail.html
git commit -m "feat: add Bootstrap 5 photo carousel to room detail"
```

---

### Task 6: Write and run tests

**Files:**
- Modify: `rooms/tests.py`

- [ ] **Step 1: Write tests**

Full content of `rooms/tests.py`:

```python
from django.test import TestCase
from unittest.mock import MagicMock

from .views import _room_photos


def _mock_room(cover_url=None, extra_urls=None):
    room = MagicMock()
    room.photo = MagicMock() if cover_url else None
    if cover_url:
        room.photo.url = cover_url
    extras = []
    for url in (extra_urls or []):
        rp = MagicMock()
        rp.photo.url = url
        extras.append(rp)
    room.photos.all.return_value = extras
    return room


class RoomPhotosHelperTest(TestCase):
    def test_no_photos_returns_empty_list(self):
        room = _mock_room()
        self.assertEqual(_room_photos(room), [])

    def test_only_cover_photo(self):
        room = _mock_room(cover_url='/media/rooms/cover.jpg')
        self.assertEqual(_room_photos(room), ['/media/rooms/cover.jpg'])

    def test_cover_plus_extra_photos(self):
        room = _mock_room(
            cover_url='/media/rooms/cover.jpg',
            extra_urls=['/media/rooms/extra1.jpg', '/media/rooms/extra2.jpg'],
        )
        self.assertEqual(_room_photos(room), [
            '/media/rooms/cover.jpg',
            '/media/rooms/extra1.jpg',
            '/media/rooms/extra2.jpg',
        ])

    def test_only_extra_photos_no_cover(self):
        room = _mock_room(extra_urls=['/media/rooms/extra.jpg'])
        self.assertEqual(_room_photos(room), ['/media/rooms/extra.jpg'])
```

- [ ] **Step 2: Run tests**

```bash
python manage.py test rooms.tests.RoomPhotosHelperTest -v 2
```
Expected: `4 tests, 0 failures`

- [ ] **Step 3: Commit**

```bash
git add rooms/tests.py
git commit -m "test: add tests for _room_photos helper"
```
