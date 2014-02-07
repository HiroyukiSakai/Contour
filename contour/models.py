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

from django.db import models


class Image(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    url = models.URLField(blank=True)
    image = models.ImageField(upload_to='images/')
    edge_image = models.ImageField(upload_to='edge_images/', blank=True)
    canny_sigma = models.FloatField(default=2)
    canny_low_threshold = models.FloatField(default=.1)
    canny_high_threshold = models.FloatField(default=.2)
    max_hausdorff_distance = models.FloatField(blank=True, null=True)

    def __unicode__(self):
        return self.title + ' (' + str(self.image) + ')'

    def delete(self, *args, **kwargs):
        image_storage, image_path = self.image.storage, self.image.path
        edge_image_storage, edge_image_path = self.edge_image.storage, self.edge_image.path
        # Delete the model before the file
        super(Image, self).delete(*args, **kwargs)
        # Delete the file after the model
        image_storage.delete(image_path)
        edge_image_storage.delete(edge_image_path)

class Track(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    images = models.ManyToManyField(Image, through='TrackImage')

    def __unicode__(self):
        return self.title

class TrackImage(models.Model):
    track = models.ForeignKey(Track)
    image = models.ForeignKey(Image)
    order = models.IntegerField()

    ordering = ['order']

    class Meta:
        ordering = ('order',)

class Player(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name

class TrackSession(models.Model):
    player = models.ForeignKey(Player, blank=True, null=True)
    track = models.ForeignKey(Track)
    score = models.FloatField()
    session_key = models.CharField(max_length=32)
    datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        string = str(self.datetime) + ' '
        if self.player:
            string += str(self.player) + ': '
        string += str(self.track)
        return string

class Drawing(models.Model):
    player = models.ForeignKey(Player, blank=True, null=True)
    image = models.ForeignKey(Image)
    drawing = models.ImageField(upload_to='drawings/')
    hausdorff_distance = models.FloatField()
    score = models.FloatField()
    datetime = models.DateTimeField(auto_now=True)
    track_session = models.ForeignKey(TrackSession, blank=True, null=True)
    track_session_index = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        string = str(self.datetime) + ' '
        if self.player:
            string += str(self.player) + ': '
        string += self.image.title
        return string

    def delete(self, *args, **kwargs):
        drawing_storage, drawing_path = self.drawing.storage, self.drawing.path
        # Delete the model before the file
        super(Drawing, self).delete(*args, **kwargs)
        # Delete the file after the model
        drawing_storage.delete(drawing_path)
