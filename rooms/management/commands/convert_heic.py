import io
import os
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from rooms.models import Room


class Command(BaseCommand):
    help = 'Converts existing HEIC photos to JPEG'

    def handle(self, *args, **options):
        from PIL import Image
        converted = 0
        for room in Room.objects.exclude(photo=''):
            if not room.photo:
                continue
            try:
                img = Image.open(room.photo.path)
                if img.format != 'HEIF':
                    continue
                img = img.convert('RGB')
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=90)
                name = os.path.splitext(os.path.basename(room.photo.name))[0] + '.jpg'
                room.photo.delete(save=False)
                room.photo.save(name, ContentFile(buffer.getvalue()), save=True)
                converted += 1
                self.stdout.write(f'  Konvertováno: {room.name}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Chyba u {room.name}: {e}'))
        self.stdout.write(self.style.SUCCESS(f'Hotovo — konvertováno {converted} fotek'))
