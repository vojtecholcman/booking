# Kóřova chata — Design Spec

**Datum:** 2026-05-26  
**Účel:** Rezervační systém pro akci 30.–31.5. Vtipná kopie booking.com pro přátele.

---

## Přehled

Webová aplikace v Djangu, která umožňuje přátelům rezervovat pokoje na akci. Celý web je za heslem (jedno sdílené heslo). Žádná registrace, žádné uživatelské účty pro veřejnost. Admin pro majitele ke správě pokojů a rezervací.

---

## Tech stack

| Technologie | Účel |
|---|---|
| Django 5.x | Web framework |
| PostgreSQL | Databáze |
| django-jazzmin | Hezčí admin UI |
| Pillow | Nahrávání a zpracování fotek |
| WhiteNoise | Servírování statických souborů |
| Gunicorn | WSGI server pro produkci |
| os.environ + .env | Konfigurace (hesla, DB přístupy) |

---

## Vizuální styl

- Věrná kopie booking.com: tmavě modrý header (#003580), bílé karty pokojů, modrá CTA tlačítka (#0071c2)
- Branding: **Kóřova chata** (všude místo "booking.com")
- Jazyk UI: čeština
- Responzivní design (mobile-friendly)

---

## Datové modely

### Room (Pokoj)
```python
name         CharField       # "Pokoj č. 1 – Modrý"
description  TextField       # popis pokoje
max_guests   PositiveIntegerField  # max. počet hostů
photo        ImageField      # fotka, uložená do media/rooms/
is_active    BooleanField    # zobrazit/skrýt pokoj (default True)
```

Computed property:
- `current_guest_count` → `sum(r.guests.count() for r in room.reservations.all())`
- `is_full` → `current_guest_count >= max_guests`

### Reservation (Rezervace)
```python
room        ForeignKey(Room, on_delete=CASCADE)
created_at  DateTimeField(auto_now_add=True)
```

### Guest (Host)
```python
reservation  ForeignKey(Reservation, on_delete=CASCADE, related_name='guests')
name         CharField  # jméno hosta
```

Obsazenost pokoje = `sum(reservation.guests.count() for reservation in room.reservations.all())`.

---

## Ochrana heslem

Vlastní Django middleware (`PasswordProtectMiddleware`):
- Při každém requestu zkontroluje `request.session['authenticated']`
- Pokud není autentizovaný → redirect na `/login/`
- Výjimky (bez hesla dostupné): `/login/`, `/admin/*`, statické a media soubory
- Heslo uložené v `os.environ['SITE_PASSWORD']`
- Po správném heslu: `request.session['authenticated'] = True` → redirect na `/`

---

## URL struktura

### Veřejné stránky (za heslem)
```
GET  /login/         → login stránka (formulář s heslem)
POST /login/         → ověření hesla, redirect na /
GET  /logout/        → smaže session, redirect na /login/
GET  /               → seznam všech aktivních pokojů
GET  /room/<id>/     → detail pokoje + rezervační formulář
POST /room/<id>/     → zpracování rezervace
GET  /confirm/<id>/  → potvrzovací stránka (id = reservation.id)
```

### Admin (Django superuser)
```
/admin/              → Django admin přihlášení
/admin/rooms/        → CRUD pokojů, nahrávání fotek
/admin/reservations/ → přehled rezervací (hosté jako inline)
```

---

## Rezervační formulář (UX)

Na stránce `/room/<id>/`:
1. Zobrazí se fotka, název, popis, kapacita a seznam aktuálně rezervovaných jmen
2. Pokud `is_full` → zobrazí se badge "Obsazeno", formulář se nezobrazí
3. Jinak: dynamický formulář s poli pro jména hostů
   - Defaultně 1 pole "Jméno hosta 1"
   - Tlačítko "+ Přidat dalšího hosta" přidá další pole (vanilla JS)
   - Tlačítko "×" na každém poli (kromě prvního) ho odstraní
   - Validace: max. počet polí = zbývající kapacita
4. Submit → POST → vytvoří `Reservation` + `Guest` záznamy → redirect na `/confirm/<id>/`

---

## Admin panel (django-jazzmin)

### Správa pokojů
- Seznam pokojů s náhledem fotky, názvem, kapacitou, obsazeností
- Formulář pro přidání/úpravu: všechna pole včetně nahrání fotky
- Možnost aktivovat/deaktivovat pokoj (skrýt ze seznamu)

### Správa rezervací
- Seznam rezervací: pokoj, hosté (všechna jména), čas vytvoření
- Možnost smazat rezervaci (uvolní místo)
- Možnost editovat jména hostů inline

---

## Deployment

```
[prohlížeč kamaráda]
       ↓
[Cloudflare tunnel]
       ↓
[Gunicorn @ 127.0.0.1:8000]
       ↓
[Django app]
       ↓
[PostgreSQL @ localhost]
```

- Statické soubory: WhiteNoise (integrováno v Djangu, žádný Nginx)
- Media soubory (fotky): v `urls.py` přidáme `+ static(MEDIA_URL, document_root=MEDIA_ROOT)` — funguje i v produkci pro tento use case (nízká návštěvnost)
- Konfigurace přes `.env` soubor (není v gitu)
- `ALLOWED_HOSTS` obsahuje doménu z Cloudflare tunnel

### Proměnné prostředí (.env)
```
SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=kóřovachata.vasedomena.com
DB_NAME=korova_chata
DB_USER=...
DB_PASSWORD=...
DB_HOST=localhost
DB_PORT=5432
SITE_PASSWORD=...   # heslo pro přátele
```

---

## Struktura projektu

```
booking/
├── manage.py
├── .env                    # není v gitu
├── .gitignore
├── requirements.txt
├── korova_chata/           # Django projekt (settings, urls, wsgi)
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── middleware.py       # PasswordProtectMiddleware
├── rooms/                  # Django app
│   ├── models.py           # Room, Reservation, Guest
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── templates/rooms/
│       ├── base.html       # booking.com styl, header Kóřova chata
│       ├── login.html
│       ├── room_list.html
│       ├── room_detail.html
│       └── confirm.html
└── media/                  # nahrané fotky (není v gitu)
```

---

## Co není v scope

- Email notifikace
- Platby
- Výběr datumů (datum je pevné: 30.–31.5.)
- Více akcí
- Uživatelské účty pro hosty
- Export dat
