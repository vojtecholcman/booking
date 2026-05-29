from django.test import TestCase
from unittest.mock import MagicMock

from rooms.views import _room_photos


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
