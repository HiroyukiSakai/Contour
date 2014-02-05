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

from django.contrib import admin

from .models import *


class TrackImageInline(admin.TabularInline):
    model = Track.images.through

    ordering = ['order']

class TrackAdmin(admin.ModelAdmin):
    inlines = [TrackImageInline]

admin.site.register(Track, TrackAdmin)
admin.site.register(Image)
admin.site.register(TrackSession)
admin.site.register(Drawing)
admin.site.register(Player)
