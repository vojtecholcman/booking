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
