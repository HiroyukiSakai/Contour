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

"""Describes the models used in Contour.

.. moduleauthor:: Hiroyuki Sakai <hiroyuki.sakai@student.tuwien.ac.at>

"""

from django.db import models


class Image(models.Model):
    """
    Stores a single image which serves as a template for :class:`.Drawing` objects .

    """
    title = models.CharField(max_length=255)
    """The title of the image."""

    author = models.CharField(max_length=255, blank=True)
    """Optional author of the image (e.g. Pablo Picasso)."""

    url = models.URLField(blank=True)
    """Optional link to additional information."""

    image = models.ImageField(upload_to='images/')
    """:class:`django.db.models.ImageField` to the image on the filesystem."""

    edge_image = models.ImageField(upload_to='edge_images/', blank=True)
    """:class:`django.db.models.ImageField` to the edge image on the filesystem. The edge image is calculated automatically."""

    dilated_edge_image = models.ImageField(upload_to='dilated_edge_images/', blank=True)
    """:class:`django.db.models.ImageField` to the dilated edge image on the filesystem. The dilated edge image is used to assess the score of a drawing."""

    canny_sigma = models.FloatField(default=2)
    """The sigma value for the Gaussian blur which is performed before the Canny edge detection."""

    canny_low_threshold = models.FloatField(default=.1)
    """The low threshold for the Canny edge detection."""

    canny_high_threshold = models.FloatField(default=.2)
    """The high threshold for the Canny edge detection."""

    max_distance = models.FloatField(blank=True, null=True)
    """This is a value which is used for the score calculation."""

    def __unicode__(self):
        return self.title + ' (' + str(self.image) + ')'

    def delete(self, *args, **kwargs):
        """Deletes the :class:`.Image` object along with its associated files."""
        image_storage, image_path = self.image.storage, self.image.path
        edge_image_storage, edge_image_path = self.edge_image.storage, self.edge_image.path
        # Delete the model before the file
        super(Image, self).delete(*args, **kwargs)
        # Delete the file after the model
        image_storage.delete(image_path)
        edge_image_storage.delete(edge_image_path)

class Track(models.Model):
    """
    Stores a track which is a set of :class:`.Image` objects  supposed to be drawn in succession.

    """
    title = models.CharField(max_length=255)
    description = models.TextField()
    images = models.ManyToManyField(Image, through='TrackImage')

    def __unicode__(self):
        return self.title

class TrackImage(models.Model):
    """
    Stores a many-to-many (n-to-n) relation between :class:`.Track` objects  and :class:`.Image` objects.

    """

    track = models.ForeignKey(Track)
    """The reference to the :class:`.Track` object."""

    image = models.ForeignKey(Image)
    """The reference to the :class:`.Image` object."""

    order = models.IntegerField()
    """The index of a :class:`.Image` object inside a :class:`.Track`."""

    ordering = ['order']

    class Meta:
        ordering = ('order',)

class Player(models.Model):
    """
    Stores a player which can be associated to :class:`.TrackSession` and :class:`.Drawing` objects.

    """
    name = models.CharField(max_length=255, unique=True)
    """The name of the player."""

    def __unicode__(self):
        return self.name

class TrackSession(models.Model):
    """
    Stores a track sesssion which stores the specific track session of a player.

    """
    player = models.ForeignKey(Player, blank=True, null=True)
    """The reference to a :class:`.Player` object."""

    track = models.ForeignKey(Track)
    """The reference to a :class:`.Track` object."""

    score = models.FloatField()
    """The attained score."""

    session_key = models.CharField(max_length=32)
    """The associated session key of the user associated."""

    datetime = models.DateTimeField(auto_now_add=True)
    """The creation time of the track session."""

    def __unicode__(self):
        string = str(self.datetime) + ' '
        if self.player:
            string += str(self.player) + ': '
        string += str(self.track)
        return string

class Drawing(models.Model):
    """
    Stores a drawing conducted by a player.

    """
    player = models.ForeignKey(Player, blank=True, null=True)
    """The reference to the :class:`.Player` object who was drawn the drawing."""

    image = models.ForeignKey(Image)
    """The reference to the :class:`.Image` object which is the template for the drawing."""

    drawing = models.ImageField(upload_to='drawings/')
    """:class:`django.db.models.ImageField` to the drawing on the filesystem."""

    distance = models.FloatField()
    """The distance of between the drawing and the original (edge) image."""

    score = models.FloatField()
    """The attained score for the drawing."""

    datetime = models.DateTimeField(auto_now=True)
    """The modification time for the drawing."""

    track_session = models.ForeignKey(TrackSession, blank=True, null=True)
    """The reference to the :class:`.TrackSession` (optional)."""

    track_session_index = models.IntegerField(blank=True, null=True)
    """The index of the drawing inside a :class:`.TrackSession`.."""

    def __unicode__(self):
        string = str(self.datetime) + ' '
        if self.player:
            string += str(self.player) + ': '
        string += self.image.title
        return string

    def delete(self, *args, **kwargs):
        """Deletes the :class:`.Drawing` object along with its associated files."""
        drawing_storage, drawing_path = self.drawing.storage, self.drawing.path
        # Delete the model before the file
        super(Drawing, self).delete(*args, **kwargs)
        # Delete the file after the model
        drawing_storage.delete(drawing_path)
