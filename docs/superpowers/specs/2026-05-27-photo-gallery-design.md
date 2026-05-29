# Photo Gallery — Design spec
Date: 2026-05-27

## Overview

Add support for multiple photos per room. The detail page shows a Bootstrap 5 carousel. The list page (room cards) is unchanged — it continues to show `Room.photo` as the cover image.

## Data model

### New model: `RoomPhoto`

```python
class RoomPhoto(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='rooms/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'pk']
```

- `Room.photo` stays as-is — used as cover photo on the list page.
- `RoomPhoto` holds additional photos shown in the carousel on the detail page.
- HEIC→JPEG conversion logic is extracted into a shared helper function (`_convert_heic_to_jpeg`) and used by both `Room.save()` and `RoomPhoto.save()`.

## Admin

`RoomPhoto` registered as `TabularInline` under `RoomAdmin`. Admins can add/remove/reorder extra photos directly on the room edit page.

## Carousel behavior (detail page)

The carousel is built from: `Room.photo` (first slide, if set) + all `RoomPhoto` objects ordered by `order`, then `pk`.

- If there is exactly 1 photo total: show a plain `<img>`, no carousel controls.
- If there are 2+ photos: show Bootstrap 5 carousel with prev/next arrows and dot indicators.
- If there are no photos at all: show the emoji placeholder (`🛏️`).

## Templates

### `room_list.html`
No changes. Continues to show `room.photo` as the card image.

### `room_detail.html`
Replace the single `<img>` block with a carousel block. The view passes a `photos` list (built from `Room.photo` + `RoomPhoto` queryset) to the template.

## View changes

`room_detail` view builds the `photos` list:

```python
photos = []
if room.photo:
    photos.append(room.photo.url)
for rp in room.photos.all():
    photos.append(rp.photo.url)
context['photos'] = photos
```

## Migration

`0002_roomphoto.py` — creates the `RoomPhoto` table. No data migration needed; existing rooms keep their `Room.photo` as cover.

## Out of scope

- Carousel on the list page
- Reordering via drag-and-drop in admin
- Photo deletion from the detail page (admin only)
- Lightbox / fullscreen view
