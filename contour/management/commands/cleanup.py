'''
    Contour  Copyright (C) 2013-2014  Hiroyuki Sakai

    This file is part of Contour.

    Contour is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Contour is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Contour.  If not, see <http://www.gnu.org/licenses/>.
'''

# delete images without tracks and drawings

import os, time

from datetime import datetime

from django.core.management.base import BaseCommand
from contour.models import *
from Contour import settings


class Command(BaseCommand):
    help = 'Cleans the database and filesystem from unreferenced items.'

    def handle(self, *args, **options):

        self.stdout.write('Deleting unreferenced track sessions ...\n')

        track_sessions = TrackSession.objects.filter(player__isnull=True, datetime__lt=datetime.fromtimestamp(time.time() - 24 * 60 * 60))
        for track_session in track_sessions:
            self.stdout.write('TrackSession:' + ' ' + str(track_session) + '\n')

            # delete referenced drawings
            drawings = Drawing.objects.filter(track_session=track_session, player__isnull=True);
            for drawing in drawings:
                self.stdout.write(' Drawing:' + ' ' + str(drawing) + '\n')

            drawings.delete()
            track_session.delete()


        self.stdout.write('Deleting unreferenced single drawings ...\n')

        drawings = Drawing.objects.filter(track_session__isnull=True, player__isnull=True)
        for drawing in drawings:
            self.stdout.write(' Drawing:' + ' ' + str(drawing) + '\n')
        drawings.delete()


        self.stdout.write('Deleting unreferenced images ...\n')

        images = Image.objects.filter(track__isnull=True, drawing__isnull=True)
        for image in images:
            self.stdout.write('Image:' + ' ' + str(image) + '\n')
        images.delete()


        self.stdout.write('Deleting unreferenced files ...\n')

        images_dir = 'images'
        edge_images_dir = 'edge_images'
        drawings_dir = 'drawings'

        for filename in os.listdir(os.path.join(settings.MEDIA_ROOT, images_dir)):
            try:
                image = Image.objects.get(image=os.path.join(images_dir, filename))
            except Image.DoesNotExist:
                filepath = os.path.join(settings.MEDIA_ROOT, images_dir, filename)
                self.stdout.write(filepath + '\n')
                os.remove(filepath)

        for filename in os.listdir(os.path.join(settings.MEDIA_ROOT, edge_images_dir)):
            try:
                image = Image.objects.get(edge_image=os.path.join(edge_images_dir, filename))
            except Image.DoesNotExist:
                filepath = os.path.join(settings.MEDIA_ROOT, edge_images_dir, filename)
                self.stdout.write(filepath + '\n')
                os.remove(filepath)

        for filename in os.listdir(os.path.join(settings.MEDIA_ROOT, drawings_dir)):
            try:
                drawing = Drawing.objects.get(drawing=os.path.join(drawings_dir, filename))
            except Drawing.DoesNotExist:
                filepath = os.path.join(settings.MEDIA_ROOT, drawings_dir, filename)
                self.stdout.write(filepath + '\n')
                os.remove(filepath)
