# Kóřova chata — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rezervační systém pro akci 30.–31.5. — věrná kopie booking.com s brandingem "Kóřova chata", heslem chráněný web, Django + PostgreSQL.

**Architecture:** Jeden Django projekt (`korova_chata`) s jednou app (`rooms`). Vlastní middleware kontroluje session heslo před každým requestem. Veřejná část napodobuje booking.com, admin panel přes django-jazzmin. Fotky uložené na disku v `media/`.

**Tech Stack:** Django 5.1, PostgreSQL + psycopg2-binary, django-jazzmin, Pillow, WhiteNoise, Gunicorn

---

## ⚡ Setup na novém počítači

```bash
git clone <repo-url> booking
cd booking
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Vytvoř `.env` (není v gitu, musíš vytvořit ručně):
```
SECRET_KEY=k7)^(odc_r$iza3!%)j&&yqiu#l5oiosh-59o5!!#(b@u)^9d-
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=korova_chata
DB_USER=postgres
DB_PASSWORD=korova123
DB_HOST=localhost
DB_PORT=5432
SITE_PASSWORD=heslo
```

Spusť databázi přes Docker:
```bash
docker compose up db -d
```

Spusť migrace:
```bash
python manage.py migrate
```

---

## Aktuální stav (2026-05-26)

| Task | Stav | Commit |
|---|---|---|
| Task 1: Project Scaffold | ✅ HOTOVO | `2ffce81`, `c60aa88` |
| Task 2: Models + Tests | ✅ HOTOVO | `af854a6` |
| Task 3: Password Middleware | ⏳ TODO | — |
| Task 4: Views + URLs | ⏳ TODO | — |
| Task 5: Templates | ⏳ TODO | — |
| Task 6: Admin | ⏳ TODO | — |
| Task 7: Deployment | ⏳ TODO | — |

**Poznámky k hotovým taskům:**
- `docker-compose.yaml` přidán (`be77eb7`) — DB na portu 5432, user `postgres`, password `korova123`, db `korova_chata`
- `.env` soubor existuje lokálně (není v gitu) — viz Setup sekce výše
- `settings.py` má CSRF_TRUSTED_ORIGINS pro Cloudflare tunnel a `.env` loading
- Modely `Room`, `Reservation`, `Guest` jsou implementované s migrací `0001_initial`

---

## Soubory

```
booking/
├── manage.py
├── requirements.txt
├── .env                    (není v gitu — viz setup)
├── .env.example
├── .gitignore
├── docker-compose.yaml
├── korova_chata/
│   ├── __init__.py
│   ├── settings.py         ✅ hotovo
│   ├── urls.py             ⏳ zatím placeholder
│   ├── wsgi.py
│   └── middleware.py       ⏳ zatím passthrough placeholder
├── rooms/
│   ├── __init__.py
│   ├── models.py           ✅ hotovo
│   ├── views.py            ⏳ zatím placeholder
│   ├── urls.py             ⏳ neexistuje
│   ├── admin.py            ⏳ zatím placeholder
│   ├── migrations/
│   │   └── 0001_initial.py ✅ hotovo
│   ├── templates/
│   │   └── rooms/          ⏳ neexistuje
│   └── tests/
│       ├── __init__.py     ✅ hotovo
│       ├── test_models.py  ✅ hotovo
│       ├── test_middleware.py ⏳ prázdný
│       └── test_views.py   ⏳ prázdný
└── media/                  (není v gitu)
```

---

## ~~Task 1: Project Scaffold~~ ✅ HOTOVO

Commitnuto v `2ffce81` a `c60aa88`. Obsahuje:
- `requirements.txt`, `.gitignore`, `.env.example`
- `korova_chata/settings.py` s jazzmin, WhiteNoise, PostgreSQL, SITE_PASSWORD, CSRF_TRUSTED_ORIGINS, `.env` loading
- `korova_chata/middleware.py` — passthrough placeholder
- Django projekt a rooms app scaffold

---

## ~~Task 2: Models + Tests~~ ✅ HOTOVO

Commitnuto v `af854a6`. Obsahuje:
- `rooms/models.py` — Room (name, description, max_guests, photo, is_active, current_guest_count, is_full, remaining_capacity), Reservation (room FK, created_at), Guest (reservation FK, name)
- `rooms/migrations/0001_initial.py`
- `rooms/tests/test_models.py` — 10 testů, všechny prochází

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
mkdir rooms\templates\rooms
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

- [ ] **Step 7: Ověř v prohlížeči**

```bash
python manage.py runserver
```

Zkontroluj:
- http://localhost:8000/login/ — přihlašovací formulář, heslo `heslo`
- http://localhost:8000/ — seznam pokojů (prázdný, žádné pokoje ještě)
- http://localhost:8000/admin/ — Django admin

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

- [ ] **Step 3: Spusť server a ověř admin panel**

Otevři http://localhost:8000/admin/ — přidej testovací pokoj s fotkou a ověř že se zobrazí na http://localhost:8000/

- [ ] **Step 4: Ověř celý flow**

1. Přihlaš se heslem `heslo`
2. Vyber pokoj → klikni Rezervovat
3. Přidej 2 jména → odešli
4. Zkontroluj potvrzovací stránku
5. Zkontroluj v adminu že rezervace přibyla

- [ ] **Step 5: Commit**

```bash
git add rooms/admin.py
git commit -m "feat: configure Django admin with jazzmin for rooms and reservations"
```

---

## Task 7: Deployment Configuration

**Files:**
- Create: `media/.gitkeep`
- Modify: `korova_chata/settings.py` (přidat .env loading — pokud ještě není)

**Poznámka:** `.env` loading je již v `settings.py` z commitu `c60aa88`. Step 3 níže lze přeskočit pokud `settings.py` začíná blokem s `_env_path`.

- [ ] **Step 1: Vytvoř `media/.gitkeep`**

```bash
mkdir media
type nul > media\.gitkeep
```

- [ ] **Step 2: Vytvoř produkční `.env` na serveru**

```
SECRET_KEY=<vygeneruj: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
DEBUG=False
ALLOWED_HOSTS=tvoje-domena.trycloudflare.com,localhost
DB_NAME=korova_chata
DB_USER=postgres
DB_PASSWORD=korova123
DB_HOST=localhost
DB_PORT=5432
SITE_PASSWORD=tvoje-heslo-pro-kamarady
```

- [ ] **Step 3: Ověř, že `settings.py` načítá `.env`**

Soubor by měl začínat:
```python
import os
from pathlib import Path

_env_path = Path(__file__).resolve().parent.parent / '.env'
if _env_path.exists():
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _key, _, _val = _line.partition('=')
                os.environ.setdefault(_key.strip(), _val.strip())
```

Pokud ne, přidej tento blok na začátek souboru (před `BASE_DIR`).

- [ ] **Step 4: Sesbírej statické soubory**

```bash
python manage.py collectstatic --noinput
```

- [ ] **Step 5: Ověř produkční spuštění**

```bash
gunicorn korova_chata.wsgi:application --bind 127.0.0.1:8000 --workers 2
```

Otevři http://localhost:8000/ — musí fungovat s `DEBUG=False`.

- [ ] **Step 6: Spusť testy naposledy**

```bash
python manage.py test rooms -v 2
```

- [ ] **Step 7: Commit**

```bash
git add media/.gitkeep
git commit -m "feat: add media dir, finalize deployment config"
```

---

## Cloudflare Tunnel

```bash
cloudflared tunnel --url http://127.0.0.1:8000
```

Doménu z výstupu přidej do `.env` jako `ALLOWED_HOSTS=domena.trycloudflare.com,localhost`.

---

## Checklist pokrytí specifikace

| Požadavek | Task | Stav |
|---|---|---|
| Django + PostgreSQL | Task 1 | ✅ |
| Heslem chráněný web | Task 3 | ⏳ |
| Admin: pokoje, fotky, kapacita | Task 6 | ⏳ |
| Admin: smazat/upravit rezervaci | Task 6 | ⏳ |
| Veřejná část: seznam pokojů | Task 4, 5 | ⏳ |
| Rezervace: jméno + více hostů | Task 4, 5 | ⏳ |
| Obsazeno badge | Task 4, 5 | ⏳ |
| Booking.com vizuální styl | Task 5 | ⏳ |
| Kóřova chata branding | Task 5 | ⏳ |
| Cloudflare tunnel | Task 7 | ⏳ |
| Datum akce pevné (30.–31.5.) | Task 5 | ⏳ |
