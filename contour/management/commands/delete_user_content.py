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

import os

from django.core.management.base import BaseCommand
from contour.models import *
from Contour import settings


class Command(BaseCommand):
    help = 'Deletes all user content. Handle with care.'

    def handle(self, *args, **options):

        self.stdout.write('Deleting track sessions ...\n')

        track_sessions = TrackSession.objects.all()
        for track_session in track_sessions:
            self.stdout.write('TrackSession:' + ' ' + str(track_session) + '\n')
        track_sessions.delete()


        self.stdout.write('Deleting drawings ...\n')

        drawings = Drawing.objects.all()
        for drawing in drawings:
            self.stdout.write('Drawing:' + ' ' + str(drawing) + '\n')
        drawings.delete()


        self.stdout.write('Deleting players ...\n')

        players = Player.objects.all()
        for player in players:
            self.stdout.write('Player:' + ' ' + str(player) + '\n')
        players.delete()


        self.stdout.write('Deleting files ...\n')

        drawings_dir = 'drawings'

        for filename in os.listdir(os.path.join(settings.MEDIA_ROOT, drawings_dir)):
            filepath = os.path.join(settings.MEDIA_ROOT, drawings_dir, filename)
            self.stdout.write(filepath + '\n')
            os.remove(filepath)
