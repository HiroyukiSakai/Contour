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
