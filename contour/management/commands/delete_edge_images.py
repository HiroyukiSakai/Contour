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
    help = 'Deletes all edge images.'

    def handle(self, *args, **options):

        self.stdout.write('Deleting edge images ...\n')

        images = Image.objects.all()
        for image in images:
            self.stdout.write('Edge image:' + ' ' + str(image) + '\n')
            if image.edge_image:
                image.edge_image.delete()
            image.max_hausdorff_distance = None
            image.save()


        self.stdout.write('Deleting files ...\n')

        edge_images_dir = 'edge_images'

        for filename in os.listdir(os.path.join(settings.MEDIA_ROOT, edge_images_dir)):
            filepath = os.path.join(settings.MEDIA_ROOT, edge_images_dir, filename)
            self.stdout.write(filepath + '\n')
            os.remove(filepath)
