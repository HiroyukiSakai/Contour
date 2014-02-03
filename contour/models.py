from django.db import models


class Image(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    url = models.URLField(blank=True)
    image = models.ImageField(upload_to='images/')
    edge_image = models.ImageField(upload_to='edge_images/', blank=True)
    canny_sigma = models.FloatField(default=1)
    canny_low_threshold = models.FloatField(default=.1)
    canny_high_threshold = models.FloatField(default=.2)
    max_hausdorff_distance = models.FloatField(blank=True, null=True)

    def __unicode__(self):
        return self.title + ' (' + str(self.image) + ')'

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
    datetime = models.DateTimeField(auto_now=True)

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
