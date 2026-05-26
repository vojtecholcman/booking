# Kóřova chata — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rezervační systém pro akci 30.–31.5. — věrná kopie booking.com s brandingem "Kóřova chata", heslem chráněný web, Django + PostgreSQL.

**Architecture:** Jeden Django projekt (`korova_chata`) s jednou app (`rooms`). Vlastní middleware kontroluje session heslo před každým requestem. Veřejná část napodobuje booking.com, admin panel přes django-jazzmin. Fotky uložené na disku v `media/`.

**Tech Stack:** Django 5.1, PostgreSQL + psycopg2-binary, django-jazzmin, Pillow, WhiteNoise, Gunicorn

---

## Soubory

```
booking/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── pytest.ini                          (nový)
├── korova_chata/
│   ├── __init__.py
│   ├── settings.py                     (nový)
│   ├── urls.py                         (nový)
│   ├── wsgi.py
│   └── middleware.py                   (nový)
├── rooms/
│   ├── __init__.py
│   ├── models.py                       (nový)
│   ├── views.py                        (nový)
│   ├── urls.py                         (nový)
│   ├── admin.py                        (nový)
│   ├── templates/
│   │   └── rooms/
│   │       ├── base.html               (nový)
│   │       ├── login.html              (nový)
│   │       ├── room_list.html          (nový)
│   │       ├── room_detail.html        (nový)
│   │       └── confirm.html            (nový)
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py              (nový)
│       ├── test_middleware.py          (nový)
│       └── test_views.py              (nový)
└── media/
    └── rooms/                          (fotky pokojů)
```

---

## Task 1: Project Scaffold

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `korova_chata/settings.py`

- [ ] **Step 1: Vytvoř virtuální prostředí a nainstaluj balíčky**

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install Django==5.1.7 psycopg2-binary==2.9.9 django-jazzmin==3.0.0 Pillow==10.4.0 whitenoise==6.7.0 gunicorn==22.0.0
```

- [ ] **Step 2: Vytvoř Django projekt a app**

```bash
django-admin startproject korova_chata .
python manage.py startapp rooms
```

- [ ] **Step 3: Vytvoř `requirements.txt`**

```
Django==5.1.7
psycopg2-binary==2.9.9
django-jazzmin==3.0.0
Pillow==10.4.0
whitenoise==6.7.0
gunicorn==22.0.0
```

- [ ] **Step 4: Vytvoř `.gitignore`**

```
.env
venv/
*.pyc
__pycache__/
media/
staticfiles/
*.sqlite3
.superpowers/
```

- [ ] **Step 5: Vytvoř `.env.example`**

```
SECRET_KEY=zmena-v-produkci-vygeneruj-nahodny-klic
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=korova_chata
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
SITE_PASSWORD=heslo
```

- [ ] **Step 6: Nahraď celé `korova_chata/settings.py`**

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-insecure-key-change-me')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rooms',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'korova_chata.middleware.PasswordProtectMiddleware',
]

ROOT_URLCONF = 'korova_chata.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'korova_chata.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'korova_chata'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'cs'
TIME_ZONE = 'Europe/Prague'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SITE_PASSWORD = os.environ.get('SITE_PASSWORD', 'heslo')

JAZZMIN_SETTINGS = {
    'site_title': 'Kóřova chata',
    'site_header': 'Kóřova chata',
    'site_brand': 'Kóřova chata',
    'welcome_sign': 'Správa rezervací',
    'show_ui_builder': False,
    'icons': {
        'rooms.room': 'fas fa-bed',
        'rooms.reservation': 'fas fa-calendar-check',
        'rooms.guest': 'fas fa-user',
    },
}
```

- [ ] **Step 7: Vytvoř prázdný `korova_chata/middleware.py` (placeholder, implementace v Task 3)**

```python
class PasswordProtectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)
```

- [ ] **Step 8: Vytvoř databázi v PostgreSQL a ověř připojení**

```bash
# V psql nebo pgAdmin vytvoř databázi:
createdb korova_chata -U postgres

# Ověř připojení:
python manage.py check
```

Očekávej: `System check identified no issues (0 silenced).`

- [ ] **Step 9: Commit**

```bash
git add requirements.txt .gitignore .env.example manage.py korova_chata/ rooms/
git commit -m "feat: scaffold Django project korova_chata"
```

---

## Task 2: Models + Tests

**Files:**
- Create: `rooms/tests/__init__.py`
- Create: `rooms/tests/test_models.py`
- Modify: `rooms/models.py`

- [ ] **Step 1: Vytvoř adresář pro testy a prázdný `__init__.py`**

```bash
mkdir rooms\tests
type nul > rooms\tests\__init__.py
type nul > rooms\tests\test_middleware.py
type nul > rooms\tests\test_views.py
```

- [ ] **Step 2: Napiš failing testy pro modely — `rooms/tests/test_models.py`**

```python
from django.test import TestCase
from rooms.models import Room, Reservation, Guest


class RoomModelTest(TestCase):
    def setUp(self):
        self.room = Room.objects.create(name='Modrý pokoj', max_guests=3)

    def test_str(self):
        self.assertEqual(str(self.room), 'Modrý pokoj')

    def test_current_guest_count_empty(self):
        self.assertEqual(self.room.current_guest_count, 0)

    def test_current_guest_count_with_guests(self):
        res = Reservation.objects.create(room=self.room)
        Guest.objects.create(reservation=res, name='Alice')
        Guest.objects.create(reservation=res, name='Bob')
        self.assertEqual(self.room.current_guest_count, 2)

    def test_current_guest_count_across_multiple_reservations(self):
        res1 = Reservation.objects.create(room=self.room)
        Guest.objects.create(reservation=res1, name='Alice')
        res2 = Reservation.objects.create(room=self.room)
        Guest.objects.create(reservation=res2, name='Bob')
        self.assertEqual(self.room.current_guest_count, 2)

    def test_is_not_full_when_below_capacity(self):
        res = Reservation.objects.create(room=self.room)
        Guest.objects.create(reservation=res, name='Alice')
        self.assertFalse(self.room.is_full)

    def test_is_full_when_at_capacity(self):
        res = Reservation.objects.create(room=self.room)
        for name in ['Alice', 'Bob', 'Carol']:
            Guest.objects.create(reservation=res, name=name)
        self.assertTrue(self.room.is_full)

    def test_remaining_capacity(self):
        res = Reservation.objects.create(room=self.room)
        Guest.objects.create(reservation=res, name='Alice')
        self.assertEqual(self.room.remaining_capacity, 2)

    def test_remaining_capacity_zero_when_full(self):
        res = Reservation.objects.create(room=self.room)
        for name in ['Alice', 'Bob', 'Carol']:
            Guest.objects.create(reservation=res, name=name)
        self.assertEqual(self.room.remaining_capacity, 0)


class GuestModelTest(TestCase):
    def test_str(self):
        room = Room.objects.create(name='Test', max_guests=2)
        res = Reservation.objects.create(room=room)
        guest = Guest.objects.create(reservation=res, name='Alice')
        self.assertEqual(str(guest), 'Alice')


class ReservationModelTest(TestCase):
    def test_str_includes_room_and_guests(self):
        room = Room.objects.create(name='Modrý', max_guests=3)
        res = Reservation.objects.create(room=room)
        Guest.objects.create(reservation=res, name='Alice')
        Guest.objects.create(reservation=res, name='Bob')
        self.assertIn('Modrý', str(res))
        self.assertIn('Alice', str(res))
```

- [ ] **Step 3: Spusť testy — ověř, že failují**

```bash
python manage.py test rooms.tests.test_models -v 2
```

Očekávej: chyby typu `ImportError: cannot import name 'Room'` nebo `Table doesn't exist`.

- [ ] **Step 4: Implementuj `rooms/models.py`**

```python
from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    max_guests = models.PositiveIntegerField()
    photo = models.ImageField(upload_to='rooms/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

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

    def __str__(self):
        names = ', '.join(g.name for g in self.guests.all())
        return f'{self.room.name}: {names}'


class Guest(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='guests')
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
```

- [ ] **Step 5: Vytvoř a spusť migrace**

```bash
python manage.py makemigrations rooms
python manage.py migrate
```

Očekávej výpis jako: `Creating tables... Running migrations: Applying rooms.0001_initial... OK`

- [ ] **Step 6: Spusť testy — ověř, že prochází**

```bash
python manage.py test rooms.tests.test_models -v 2
```

Očekávej: `OK` s počtem testů.

- [ ] **Step 7: Commit**

```bash
git add rooms/models.py rooms/migrations/ rooms/tests/
git commit -m "feat: add Room, Reservation, Guest models with tests"
```

---

## Task 3: Password Middleware + Tests

**Files:**
- Modify: `rooms/tests/test_middleware.py`
- Modify: `korova_chata/middleware.py`

- [ ] **Step 1: Napiš failing testy — `rooms/tests/test_middleware.py`**

Před psaním testů musí existovat alespoň prázdná URL `/` a `/login/`. Přidej do `korova_chata/urls.py` dočasně (přepíšeme v Task 4):

```python
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', lambda r: HttpResponse('login'), name='login'),
    path('', lambda r: HttpResponse('home'), name='home'),
]
```

Teď napiš testy do `rooms/tests/test_middleware.py`:

```python
from django.test import TestCase, Client


class PasswordMiddlewareTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_unauthenticated_root_redirects_to_login(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/login/')

    def test_unauthenticated_any_page_redirects_to_login(self):
        response = self.client.get('/room/1/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/login/')

    def test_login_page_accessible_without_auth(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_admin_not_redirected_to_our_login(self):
        response = self.client.get('/admin/')
        if response.status_code == 302:
            self.assertNotEqual(response['Location'], '/login/')

    def test_authenticated_session_passes_through(self):
        session = self.client.session
        session['authenticated'] = True
        session.save()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
```

- [ ] **Step 2: Spusť testy — ověř, že failují**

```bash
python manage.py test rooms.tests.test_middleware -v 2
```

Očekávej: `test_unauthenticated_root_redirects_to_login` FAIL (vrátí 200 místo 302).

- [ ] **Step 3: Implementuj `korova_chata/middleware.py`**

```python
from django.shortcuts import redirect

EXEMPT_PREFIXES = ('/login/', '/admin/', '/static/', '/media/')


class PasswordProtectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not self._is_exempt(request.path) and not request.session.get('authenticated'):
            return redirect('/login/')
        return self.get_response(request)

    def _is_exempt(self, path):
        return any(path.startswith(prefix) for prefix in EXEMPT_PREFIXES)
```

- [ ] **Step 4: Spusť testy — ověř, že prochází**

```bash
python manage.py test rooms.tests.test_middleware -v 2
```

Očekávej: `OK`.

- [ ] **Step 5: Commit**

```bash
git add korova_chata/middleware.py korova_chata/urls.py rooms/tests/test_middleware.py
git commit -m "feat: add password protect middleware with tests"
```

---

## Task 4: Views + URLs + Tests

**Files:**
- Create: `rooms/urls.py`
- Modify: `korova_chata/urls.py`
- Modify: `rooms/views.py`
- Modify: `rooms/tests/test_views.py`

- [ ] **Step 1: Napiš failing testy — `rooms/tests/test_views.py`**

```python
from django.test import TestCase, Client, override_settings
from rooms.models import Room, Reservation, Guest


class AuthHelper:
    """Mixin pro autentizaci test clienta."""
    def _auth(self):
        session = self.client.session
        session['authenticated'] = True
        session.save()


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_returns_200(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    @override_settings(SITE_PASSWORD='tajne')
    def test_correct_password_sets_session_and_redirects(self):
        response = self.client.post('/login/', {'password': 'tajne'})
        self.assertRedirects(response, '/', fetch_redirect_response=False)
        self.assertTrue(self.client.session.get('authenticated'))

    @override_settings(SITE_PASSWORD='tajne')
    def test_wrong_password_returns_200_with_error(self):
        response = self.client.post('/login/', {'password': 'spatne'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Špatné heslo')
        self.assertIsNone(self.client.session.get('authenticated'))

    @override_settings(SITE_PASSWORD='tajne')
    def test_already_authenticated_redirects_to_home(self):
        session = self.client.session
        session['authenticated'] = True
        session.save()
        response = self.client.get('/login/')
        self.assertRedirects(response, '/', fetch_redirect_response=False)


class RoomListViewTest(AuthHelper, TestCase):
    def setUp(self):
        self.client = Client()
        self._auth()

    def test_shows_active_rooms(self):
        Room.objects.create(name='Modrý', max_guests=3, is_active=True)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Modrý')

    def test_hides_inactive_rooms(self):
        Room.objects.create(name='Skrytý', max_guests=2, is_active=False)
        response = self.client.get('/')
        self.assertNotContains(response, 'Skrytý')


class RoomDetailViewTest(AuthHelper, TestCase):
    def setUp(self):
        self.client = Client()
        self._auth()
        self.room = Room.objects.create(name='Modrý', max_guests=3, is_active=True)

    def test_get_shows_room_name(self):
        response = self.client.get(f'/room/{self.room.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Modrý')

    def test_post_creates_reservation_with_guests(self):
        self.client.post(f'/room/{self.room.pk}/', {'guests': ['Alice', 'Bob']})
        self.assertEqual(self.room.reservations.count(), 1)
        self.assertEqual(self.room.reservations.first().guests.count(), 2)

    def test_post_redirects_to_confirm(self):
        response = self.client.post(f'/room/{self.room.pk}/', {'guests': ['Alice']})
        reservation = self.room.reservations.first()
        self.assertRedirects(response, f'/confirm/{reservation.pk}/', fetch_redirect_response=False)

    def test_post_empty_guests_returns_error(self):
        response = self.client.post(f'/room/{self.room.pk}/', {'guests': ['']})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Zadej alespoň jedno jméno')
        self.assertEqual(self.room.reservations.count(), 0)

    def test_full_room_post_does_not_create_reservation(self):
        res = Reservation.objects.create(room=self.room)
        for name in ['A', 'B', 'C']:
            Guest.objects.create(reservation=res, name=name)
        self.client.post(f'/room/{self.room.pk}/', {'guests': ['Dave']})
        self.assertEqual(self.room.reservations.count(), 1)

    def test_guest_count_clamped_to_remaining_capacity(self):
        res = Reservation.objects.create(room=self.room)
        Guest.objects.create(reservation=res, name='Alice')
        # room has 2 remaining, try to add 5
        self.client.post(f'/room/{self.room.pk}/', {'guests': ['B', 'C', 'D', 'E', 'F']})
        new_res = self.room.reservations.exclude(pk=res.pk).first()
        self.assertEqual(new_res.guests.count(), 2)


class ConfirmViewTest(AuthHelper, TestCase):
    def setUp(self):
        self.client = Client()
        self._auth()
        room = Room.objects.create(name='Modrý', max_guests=3, is_active=True)
        self.reservation = Reservation.objects.create(room=room)
        Guest.objects.create(reservation=self.reservation, name='Alice')

    def test_shows_guest_names(self):
        response = self.client.get(f'/confirm/{self.reservation.pk}/')
        self.assertContains(response, 'Alice')

    def test_shows_room_name(self):
        response = self.client.get(f'/confirm/{self.reservation.pk}/')
        self.assertContains(response, 'Modrý')
```

- [ ] **Step 2: Spusť testy — ověř, že failují**

```bash
python manage.py test rooms.tests.test_views -v 2
```

Očekávej: ImportError nebo 404 chyby.

- [ ] **Step 3: Implementuj `rooms/views.py`**

```python
import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from .models import Room, Guest, Reservation


def login_view(request):
    if request.session.get('authenticated'):
        return redirect('/')
    if request.method == 'POST':
        password = request.POST.get('password', '')
        if password == settings.SITE_PASSWORD:
            request.session['authenticated'] = True
            return redirect('/')
        return render(request, 'rooms/login.html', {'error': 'Špatné heslo, zkus to znovu.'})
    return render(request, 'rooms/login.html')


def logout_view(request):
    request.session.flush()
    return redirect('/login/')


def room_list(request):
    rooms = Room.objects.filter(is_active=True)
    return render(request, 'rooms/room_list.html', {'rooms': rooms})


def room_detail(request, room_id):
    room = get_object_or_404(Room, pk=room_id, is_active=True)
    guests = Guest.objects.filter(reservation__room=room).select_related('reservation')

    if request.method == 'POST':
        if room.is_full:
            return redirect(f'/room/{room_id}/')

        guest_names = [n.strip() for n in request.POST.getlist('guests') if n.strip()]
        if not guest_names:
            return render(request, 'rooms/room_detail.html', {
                'room': room,
                'guests': guests,
                'error': 'Zadej alespoň jedno jméno.',
            })

        guest_names = guest_names[:room.remaining_capacity]
        reservation = Reservation.objects.create(room=room)
        for name in guest_names:
            Guest.objects.create(reservation=reservation, name=name)

        return redirect(f'/confirm/{reservation.pk}/')

    return render(request, 'rooms/room_detail.html', {'room': room, 'guests': guests})


def confirm(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    return render(request, 'rooms/confirm.html', {'reservation': reservation})
```

- [ ] **Step 4: Vytvoř `rooms/urls.py`**

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('room/<int:room_id>/', views.room_detail, name='room_detail'),
    path('confirm/<int:reservation_id>/', views.confirm, name='confirm'),
]
```

- [ ] **Step 5: Nahraď `korova_chata/urls.py`**

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rooms import views as rooms_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', rooms_views.login_view, name='login'),
    path('logout/', rooms_views.logout_view, name='logout'),
    path('', include('rooms.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

- [ ] **Step 6: Spusť testy — ověř, že prochází**

```bash
python manage.py test rooms.tests.test_views -v 2
```

Očekávej: `OK`.

- [ ] **Step 7: Spusť všechny testy**

```bash
python manage.py test rooms -v 2
```

Očekávej: `OK` pro všechny testy.

- [ ] **Step 8: Commit**

```bash
git add rooms/views.py rooms/urls.py korova_chata/urls.py rooms/tests/test_views.py
git commit -m "feat: add views, URL routing and view tests"
```

---

## Task 5: Templates

**Files:**
- Create: `rooms/templates/rooms/base.html`
- Create: `rooms/templates/rooms/login.html`
- Create: `rooms/templates/rooms/room_list.html`
- Create: `rooms/templates/rooms/room_detail.html`
- Create: `rooms/templates/rooms/confirm.html`

- [ ] **Step 1: Vytvoř adresář pro šablony**

```bash
mkdir -p rooms\templates\rooms
```

- [ ] **Step 2: Vytvoř `rooms/templates/rooms/base.html`**

```html
<!DOCTYPE html>
<html lang="cs">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Kóřova chata</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f2f2f2; color: #333; min-height: 100vh; }
    a { color: inherit; }

    .header { background: #003580; padding: 12px 24px; display: flex; align-items: center; position: sticky; top: 0; z-index: 100; }
    .header-brand { color: #fff; font-size: 22px; font-weight: 700; text-decoration: none; letter-spacing: -0.5px; }
    .header-nav { margin-left: auto; display: flex; gap: 16px; align-items: center; }
    .header-nav a { color: #aac4e8; font-size: 13px; text-decoration: none; }
    .header-nav a:hover { color: #fff; }

    .container { max-width: 1000px; margin: 0 auto; padding: 24px 16px; }

    .btn { display: inline-block; padding: 10px 20px; border-radius: 4px; font-weight: 700; font-size: 14px; cursor: pointer; border: none; text-decoration: none; text-align: center; }
    .btn-primary { background: #0071c2; color: #fff; }
    .btn-primary:hover { background: #00487a; }
    .btn-disabled { background: #bbb; color: #fff; cursor: not-allowed; }

    input[type="text"], input[type="password"] {
      width: 100%; padding: 10px 12px; border: 1px solid #ccc; border-radius: 4px;
      font-size: 14px; outline: none;
    }
    input[type="text"]:focus, input[type="password"]:focus { border-color: #0071c2; box-shadow: 0 0 0 2px rgba(0,113,194,.15); }

    .alert-error { background: #fff0f0; color: #c00; border: 1px solid #fcc; padding: 10px 14px; border-radius: 4px; font-size: 13px; }

    .badge-full { display: inline-block; background: #c00; color: #fff; font-size: 11px; padding: 3px 8px; border-radius: 3px; font-weight: 700; }
    .badge-available { display: inline-block; background: #008009; color: #fff; font-size: 11px; padding: 3px 8px; border-radius: 3px; font-weight: 700; }

    @media (max-width: 640px) {
      .header-brand { font-size: 17px; }
    }
  </style>
</head>
<body>

<header class="header">
  <a href="/" class="header-brand">Kóřova chata</a>
  <nav class="header-nav">
    {% if request.session.authenticated %}
    <a href="/logout/">Odhlásit</a>
    {% endif %}
  </nav>
</header>

<div class="container">
  {% block content %}{% endblock %}
</div>

</body>
</html>
```

- [ ] **Step 3: Vytvoř `rooms/templates/rooms/login.html`**

```html
{% extends 'rooms/base.html' %}
{% block content %}
<div style="min-height:70vh;display:flex;align-items:center;justify-content:center;">
  <div style="background:#fff;border-radius:8px;padding:36px;width:100%;max-width:360px;box-shadow:0 2px 16px rgba(0,0,0,.15);">
    <h1 style="color:#003580;font-size:26px;font-weight:700;margin-bottom:8px;text-align:center;">Kóřova chata</h1>
    <p style="text-align:center;color:#666;font-size:13px;margin-bottom:24px;">Zadej heslo pro vstup</p>

    {% if error %}
    <div class="alert-error" style="margin-bottom:16px;">{{ error }}</div>
    {% endif %}

    <form method="post">
      {% csrf_token %}
      <label style="display:block;font-size:13px;font-weight:600;margin-bottom:6px;">Heslo</label>
      <input type="password" name="password" autofocus style="margin-bottom:16px;">
      <button type="submit" class="btn btn-primary" style="width:100%;font-size:15px;padding:12px;">Přihlásit se</button>
    </form>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 4: Vytvoř `rooms/templates/rooms/room_list.html`**

```html
{% extends 'rooms/base.html' %}
{% block content %}
<div style="margin-bottom:20px;">
  <h1 style="font-size:22px;color:#003580;margin-bottom:4px;">Vyberte si pokoj</h1>
  <p style="font-size:13px;color:#666;">Akce 30.–31. 5. &nbsp;·&nbsp; Vyberte volný pokoj a zadejte jméno.</p>
</div>

{% for room in rooms %}
<div style="background:#fff;border-radius:8px;box-shadow:0 1px 6px rgba(0,0,0,.1);margin-bottom:16px;display:flex;overflow:hidden;min-height:140px;">
  {% if room.photo %}
  <img src="{{ room.photo.url }}" alt="{{ room.name }}" style="width:200px;object-fit:cover;flex-shrink:0;">
  {% else %}
  <div style="width:200px;background:#d6e8f5;display:flex;align-items:center;justify-content:center;font-size:56px;flex-shrink:0;">🛏</div>
  {% endif %}

  <div style="padding:16px 20px;flex:1;display:flex;flex-direction:column;justify-content:space-between;">
    <div>
      <h2 style="font-size:18px;color:#003580;margin-bottom:6px;">{{ room.name }}</h2>
      {% if room.description %}
      <p style="font-size:13px;color:#555;margin-bottom:10px;">{{ room.description|truncatewords:20 }}</p>
      {% endif %}
      <p style="font-size:12px;color:#666;">
        Obsazeno: <strong>{{ room.current_guest_count }}/{{ room.max_guests }}</strong> osob
        &nbsp;
        {% if room.is_full %}
        <span class="badge-full">Obsazeno</span>
        {% else %}
        <span class="badge-available">Volno</span>
        {% endif %}
      </p>
    </div>
    <div style="margin-top:12px;">
      {% if room.is_full %}
      <span class="btn btn-disabled">Obsazeno</span>
      {% else %}
      <a href="/room/{{ room.pk }}/" class="btn btn-primary">Rezervovat</a>
      {% endif %}
    </div>
  </div>
</div>
{% empty %}
<p style="color:#666;text-align:center;margin-top:40px;">Žádné pokoje nejsou k dispozici.</p>
{% endfor %}
{% endblock %}
```

- [ ] **Step 5: Vytvoř `rooms/templates/rooms/room_detail.html`**

```html
{% extends 'rooms/base.html' %}
{% block content %}
<div style="margin-bottom:16px;">
  <a href="/" style="color:#0071c2;text-decoration:none;font-size:13px;">← Zpět na seznam pokojů</a>
</div>

<div style="display:flex;gap:24px;flex-wrap:wrap;align-items:flex-start;">

  <!-- Levá část: info o pokoji -->
  <div style="flex:2;min-width:280px;">
    {% if room.photo %}
    <img src="{{ room.photo.url }}" alt="{{ room.name }}" style="width:100%;border-radius:8px;max-height:320px;object-fit:cover;margin-bottom:20px;">
    {% else %}
    <div style="background:#d6e8f5;border-radius:8px;height:220px;display:flex;align-items:center;justify-content:center;font-size:72px;margin-bottom:20px;">🛏</div>
    {% endif %}

    <h1 style="font-size:24px;color:#003580;margin-bottom:8px;">{{ room.name }}</h1>

    {% if room.description %}
    <p style="font-size:14px;color:#555;line-height:1.6;margin-bottom:16px;">{{ room.description }}</p>
    {% endif %}

    <div style="background:#f7f7f7;border-radius:6px;padding:14px;">
      <p style="font-size:13px;font-weight:600;margin-bottom:10px;">
        Kapacita: {{ room.current_guest_count }}/{{ room.max_guests }} osob
      </p>
      {% if guests %}
      <p style="font-size:12px;color:#888;margin-bottom:6px;text-transform:uppercase;letter-spacing:.5px;">Rezervováno</p>
      {% for guest in guests %}
      <p style="font-size:13px;padding:3px 0;">👤 {{ guest.name }}</p>
      {% endfor %}
      {% endif %}
    </div>
  </div>

  <!-- Pravá část: formulář -->
  <div style="flex:1;min-width:240px;position:sticky;top:72px;">
    <div style="background:#fff;border-radius:8px;box-shadow:0 2px 12px rgba(0,0,0,.12);padding:20px;">
      <h2 style="font-size:16px;font-weight:700;margin-bottom:4px;">Vaše rezervace</h2>
      <p style="font-size:12px;color:#888;margin-bottom:16px;">Akce 30.–31. 5.</p>

      {% if room.is_full %}
      <div style="background:#fff0f0;color:#c00;border:1px solid #fcc;padding:12px;border-radius:4px;font-weight:600;font-size:14px;">
        Pokoj je plně obsazen.
      </div>
      {% else %}

      {% if error %}
      <div class="alert-error" style="margin-bottom:12px;">{{ error }}</div>
      {% endif %}

      <form method="post" id="reservation-form">
        {% csrf_token %}

        <div id="guest-fields">
          <div class="guest-row" style="display:flex;gap:6px;margin-bottom:8px;">
            <input type="text" name="guests" placeholder="Jméno hosta 1" required>
          </div>
        </div>

        {% if room.remaining_capacity > 1 %}
        <button type="button" id="add-btn" onclick="addGuest()"
          style="width:100%;background:none;border:1px dashed #0071c2;color:#0071c2;padding:7px;border-radius:4px;cursor:pointer;font-size:12px;margin-bottom:12px;">
          + Přidat dalšího hosta
        </button>
        {% endif %}

        <p style="font-size:11px;color:#888;margin-bottom:14px;">
          Zbývá volných míst: <strong id="remaining-count">{{ room.remaining_capacity }}</strong>
        </p>

        <button type="submit" class="btn btn-primary" style="width:100%;font-size:15px;padding:12px;">Rezervovat »</button>
      </form>

      <script>
        var maxGuests = {{ room.remaining_capacity }};
        var guestCount = 1;

        function addGuest() {
          if (guestCount >= maxGuests) return;
          guestCount++;
          var container = document.getElementById('guest-fields');
          var row = document.createElement('div');
          row.className = 'guest-row';
          row.style.cssText = 'display:flex;gap:6px;margin-bottom:8px;';
          var input = document.createElement('input');
          input.type = 'text';
          input.name = 'guests';
          input.placeholder = 'Jméno hosta ' + guestCount;
          input.required = true;
          input.style.cssText = 'flex:1;padding:10px 12px;border:1px solid #ccc;border-radius:4px;font-size:14px;';
          var removeBtn = document.createElement('button');
          removeBtn.type = 'button';
          removeBtn.textContent = '×';
          removeBtn.style.cssText = 'background:#fff0f0;color:#c00;border:1px solid #fcc;border-radius:4px;padding:0 12px;cursor:pointer;font-size:18px;flex-shrink:0;';
          removeBtn.onclick = function() { removeGuest(this); };
          row.appendChild(input);
          row.appendChild(removeBtn);
          container.appendChild(row);
          updateUI();
        }

        function removeGuest(btn) {
          btn.parentElement.remove();
          guestCount--;
          updateUI();
        }

        function updateUI() {
          var remaining = maxGuests - guestCount;
          document.getElementById('remaining-count').textContent = remaining;
          var addBtn = document.getElementById('add-btn');
          if (addBtn) addBtn.style.display = guestCount >= maxGuests ? 'none' : 'block';
        }
      </script>

      {% endif %}
    </div>
  </div>

</div>
{% endblock %}
```

- [ ] **Step 6: Vytvoř `rooms/templates/rooms/confirm.html`**

```html
{% extends 'rooms/base.html' %}
{% block content %}
<div style="max-width:500px;margin:60px auto;background:#fff;border-radius:8px;padding:36px;box-shadow:0 2px 16px rgba(0,0,0,.1);text-align:center;">
  <div style="font-size:52px;margin-bottom:16px;">✅</div>
  <h1 style="font-size:24px;color:#003580;margin-bottom:8px;">Rezervace potvrzena!</h1>
  <p style="color:#555;font-size:14px;margin-bottom:4px;">Pokoj: <strong>{{ reservation.room.name }}</strong></p>
  <p style="color:#888;font-size:12px;margin-bottom:24px;">Akce 30.–31. 5.</p>

  <div style="background:#f7f7f7;border-radius:6px;padding:14px;margin-bottom:24px;text-align:left;">
    <p style="font-size:12px;color:#888;margin-bottom:8px;text-transform:uppercase;letter-spacing:.5px;">Rezervovaní hosté</p>
    {% for guest in reservation.guests.all %}
    <p style="font-size:14px;padding:4px 0;">👤 {{ guest.name }}</p>
    {% endfor %}
  </div>

  <a href="/" class="btn btn-primary">Zpět na seznam pokojů</a>
</div>
{% endblock %}
```

- [ ] **Step 7: Otevři prohlížeč a ověř vizuálně**

```bash
python manage.py runserver
```

Zkontroluj:
- http://localhost:8000/login/ — zobrazí přihlašovací formulář s brandingem "Kóřova chata"
- Zadej heslo `heslo` → přesměruje na seznam pokojů (prázdný, žádné pokoje ještě)
- Admin: http://localhost:8000/admin/ — přihlásí se Django admin přihlášením

- [ ] **Step 8: Commit**

```bash
git add rooms/templates/
git commit -m "feat: add booking.com-style templates"
```

---

## Task 6: Admin Configuration

**Files:**
- Modify: `rooms/admin.py`

- [ ] **Step 1: Implementuj `rooms/admin.py`**

```python
from django.contrib import admin
from django.utils.html import format_html
from .models import Room, Reservation, Guest


class GuestInline(admin.TabularInline):
    model = Guest
    extra = 1
    fields = ['name']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'max_guests', 'guest_count_display', 'full_display', 'is_active', 'photo_preview']
    list_editable = ['is_active']
    fields = ['name', 'description', 'max_guests', 'photo', 'is_active']

    def guest_count_display(self, obj):
        return f'{obj.current_guest_count}/{obj.max_guests}'
    guest_count_display.short_description = 'Obsazenost'

    def full_display(self, obj):
        return obj.is_full
    full_display.boolean = True
    full_display.short_description = 'Plný'

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" height="40" style="border-radius:3px;" />', obj.photo.url)
        return '—'
    photo_preview.short_description = 'Foto'


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'room', 'guest_count', 'created_at']
    list_filter = ['room']
    readonly_fields = ['created_at']
    inlines = [GuestInline]

    def guest_count(self, obj):
        return obj.guests.count()
    guest_count.short_description = 'Počet hostů'
```

- [ ] **Step 2: Vytvoř superusera**

```bash
python manage.py createsuperuser
```

Zadej uživatelské jméno, email (volitelně) a heslo.

- [ ] **Step 3: Spusť server a ověř admin panel**

```bash
python manage.py runserver
```

Otevři http://localhost:8000/admin/ a ověř:
- Přihlášení superuserem funguje
- V sekci "Rooms" lze přidat pokoj s fotkou
- V sekci "Reservations" jsou inline hosté

- [ ] **Step 4: Přidej testovací pokoj přes admin**

Přidej alespoň jeden pokoj s:
- Název: libovolný
- Popis: libovolný
- Max hostů: 3–5
- Fotka: libovolná (z disku)
- Is active: zaškrtnuto

- [ ] **Step 5: Ověř veřejnou část**

Otevři http://localhost:8000/ — pokoj by měl být vidět s fotkou a tlačítkem Rezervovat.

Klikni "Rezervovat", zadej 2 jména, odešli — ověř potvrzovací stránku.

- [ ] **Step 6: Commit**

```bash
git add rooms/admin.py
git commit -m "feat: configure Django admin with jazzmin for rooms and reservations"
```

---

## Task 7: Deployment Configuration

**Files:**
- Create: `.env` (pouze lokálně, nikdy do gitu)
- Create: `media/.gitkeep`

- [ ] **Step 1: Vytvoř `media/.gitkeep`**

```bash
mkdir media 2>nul
type nul > media\.gitkeep
```

- [ ] **Step 2: Vytvoř `.env` soubor na serveru**

Soubor `.env` musí existovat na serveru (není v gitu). Příklad:

```
SECRET_KEY=generuj-nahodny-klic-napr-python-c-from-django.core.management.utils-import-get_random_secret_key-print-get_random_secret_key
DEBUG=False
ALLOWED_HOSTS=tvoje-domena.trycloudflare.com,localhost
DB_NAME=korova_chata
DB_USER=postgres
DB_PASSWORD=tvoje-db-heslo
DB_HOST=localhost
DB_PORT=5432
SITE_PASSWORD=tvoje-heslo-pro-kamarady
```

Pro vygenerování SECRET_KEY:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

- [ ] **Step 3: Nastav načítání `.env` v `korova_chata/settings.py`**

Nahraď první dva řádky souboru (`import os` a `from pathlib import Path`) tímto blokem:

```python
import os
from pathlib import Path

# Načti .env soubor pokud existuje (pro produkci)
_env_path = Path(__file__).resolve().parent.parent / '.env'
if _env_path.exists():
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _key, _, _val = _line.partition('=')
                os.environ.setdefault(_key.strip(), _val.strip())
```

Zbytek souboru zůstane beze změny — `BASE_DIR`, `SECRET_KEY` atd. jsou stále níže.

- [ ] **Step 4: Sesbírej statické soubory**

```bash
python manage.py collectstatic --noinput
```

Očekávej: soubory zkopírované do `staticfiles/`.

- [ ] **Step 5: Ověř produkční spuštění**

```bash
gunicorn korova_chata.wsgi:application --bind 127.0.0.1:8000 --workers 2
```

Otevři http://localhost:8000/ — web musí fungovat s `DEBUG=False`.

- [ ] **Step 6: Spusť všechny testy naposledy**

```bash
python manage.py test rooms -v 2
```

Očekávej: `OK`.

- [ ] **Step 7: Commit**

```bash
git add media/.gitkeep korova_chata/settings.py
git commit -m "feat: add deployment config, .env loading, media dir"
```

---

## Cloudflare Tunnel — spuštění

Po nasazení na server:

```bash
# Nainstaluj cloudflared (https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/)
cloudflared tunnel --url http://127.0.0.1:8000
```

Nebo pro permanentní tunel s vlastní doménou:
```bash
cloudflared service install
```

Doménu z Cloudflare přidej do `.env` jako `ALLOWED_HOSTS`.

---

## Checklist pokrytí specifikace

| Požadavek | Task |
|---|---|
| Django + PostgreSQL | Task 1 |
| Heslem chráněný web | Task 3 |
| Admin: přidat pokoje, fotky, kapacitu | Task 6 |
| Admin: smazat/upravit rezervaci | Task 6 |
| Veřejná část: seznam pokojů | Task 4, 5 |
| Rezervace: jméno + více hostů | Task 4, 5 |
| Obsazeno badge | Task 4, 5 |
| Booking.com vizuální styl | Task 5 |
| Kóřova chata branding | Task 5 |
| Cloudflare tunnel kompatibilita | Task 7 |
| Datum akce pevné (30.–31.5.) | Task 5 (v šablonách) |
