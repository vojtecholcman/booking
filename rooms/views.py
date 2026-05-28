from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render

from .models import TIME_SLOTS, Guest, Reservation, Room


def _room_photos(room):
    return [rp.photo.url for rp in room.photos.all()]


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
    rooms = Room.objects.filter(is_active=True).prefetch_related('reservations__guests', 'photos')
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
