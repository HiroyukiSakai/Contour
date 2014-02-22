#   Contour  Copyright (C) 2013-2014  Hiroyuki Sakai
#
#   This file is part of Contour.
#
#   Contour is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Contour is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Contour.  If not, see <http://www.gnu.org/licenses/>.

"""Describes the representation of models in the admin interface.

.. moduleauthor:: Hiroyuki Sakai <hiroyuki.sakai@student.tuwien.ac.at>

"""

from django.contrib import admin

from .models import *


class TrackImageInline(admin.TabularInline):
    """Describes the representation of images in the track admin interface.

    """
    model = Track.images.through

    ordering = ['order']

class TrackAdmin(admin.ModelAdmin):
    """Describes the representation of tracks in the admin interface.

    """
    inlines = [TrackImageInline]

class ImageAdmin(admin.ModelAdmin):
    """Describes the representation of images in the admin interface.

    """
    class Media:
        js = ['admin/js/main.js',]

    def add_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        #extra_context['show_edit_edge_image'] = True
        return super(ImageAdmin, self).add_view(request, extra_context=extra_context)

    def change_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_edit_edge_image'] = True
        return super(ImageAdmin, self).change_view(request, object_id, extra_context=extra_context)

admin.site.register(Track, TrackAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(TrackSession)
admin.site.register(Drawing)
admin.site.register(Player)
