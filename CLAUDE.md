# Kóřova chata — CLAUDE.md

Rezervační systém pro akci 30.–31.5. Vtipná kopie booking.com pro přátele.

## Tech stack

- **Django 5.x** + **PostgreSQL**
- **django-jazzmin** (admin UI)
- **Pillow** (fotky), **WhiteNoise** (statické soubory), **Gunicorn** (produkce)
- Konfigurace přes `os.environ` + `.env` soubor

## Struktura projektu

```
booking/
├── korova_chata/       # Django projekt (settings, urls, wsgi, middleware)
├── rooms/              # Django app (modely, views, šablony)
│   └── templates/rooms/
├── media/              # nahrané fotky (není v gitu)
├── docs/superpowers/specs/   # design dokumenty
└── .env                # není v gitu
```

## Modely

- **Room** — název, popis, max_guests, photo, is_active
- **Reservation** — room (FK), created_at
- **Guest** — reservation (FK), name

## Klíčová pravidla

- Celý web je za heslem (`SITE_PASSWORD` v env) — vlastní middleware
- `/admin/` je dostupné bez hesla (Django superuser)
- Hosté zadávají jen jméno (žádná registrace)
- Datum akce je pevné (30.–31.5.), žádný date picker
- Pokoj "Obsazeno" = sum(guests) >= max_guests

## Git

- Commity **bez** Co-Authored-By
- Citlivé soubory (`.env`, `media/`) jsou v `.gitignore`

## Deployment

- Gunicorn na portu 8000, Cloudflare tunnel před ním
- WhiteNoise pro statické soubory, Django URL handler pro media

## Design spec

Viz [docs/superpowers/specs/2026-05-26-korova-chata-design.md](docs/superpowers/specs/2026-05-26-korova-chata-design.md)
