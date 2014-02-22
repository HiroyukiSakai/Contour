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

"""Describes the views used in Contour.

.. moduleauthor:: Hiroyuki Sakai <hiroyuki.sakai@student.tuwien.ac.at>

"""

import base64, os, pdb, urllib

from PIL import Image as PImage

from django.core.files import File
from django.http import Http404, HttpResponse
from django.shortcuts import render

import flickrapi, numpy as np
from scipy import misc, ndimage
from skimage import filter, io, transform

import secret
from .. import settings
from .forms import *
from .models import *
from .set_metrics import *
from .util import slugify


MISSING_PIXELS_PENALTY_FACTOR = 1.
SUPERFLUOUS_PIXELS_PENALTY_FACTOR = .1


def create_session(request, view_name, id):
    """Creates a user session.

    :param request: The request object containing the user request.
    :type request: :class:`django.http.HttpRequest`.
    :param view_name: The name of the view to which the session should be associated.
    :type view_name: string.
    :param id: The id of the :class:`.models.Image` or :class:`.models.Track`.
    :type id: int.

    """
    if not request.session.get('is_playing'):
        request.session['is_playing'] = True
        request.session['view_name'] = view_name
        request.session['id'] = id

def clear_session(request):
    """Clears all varibles of the user session.

    :param request: The request object containing the user session.
    :type request: :class:`django.http.HttpRequest`.

    """
    request.session['is_playing'] = False
    request.session['view_name'] = None
    request.session['id'] = None
    request.session['image_id'] = None
    request.session['image_index'] = None
    request.session['track_session_id'] = None
    request.session['drawing_id'] = None
    request.session['last_drawing_id'] = None

def destroy_session(request):
    """Destroys a currently running user session if such a request has been sent.

    :param request: The request object containing the user request.
    :type request: :class:`django.http.HttpRequest`.
    :returns: bool -- `True` if the session was cleared, otherwise `None`.

    """
    if request.session.get('is_playing') and request.method == 'POST':
        form = DiscardSessionForm(request.POST)

        if form.is_valid() and form.cleaned_data['discard_session']:
            clear_session(request)
            return True

    return

def check_session(request, view_name=None, id=None):
    """Checks if the requested URL is in canon with the currently running session. The user will be asked if he wants to discad his session if there's a discrepancy.

    :param request: The request object containing the user request.
    :type request: :class:`django.http.HttpRequest`.
    :param view_name: The name of the requested view to which the session should be associated.
    :type view_name: string.
    :param id: The id of the requested :class:`.models.Image` or :class:`.models.Track`.
    :type id: int.
    :returns: :class:`django.http.HttpResponse` -- The rendered template as response.

    """
    if request.session.get('is_playing') and (view_name != request.session.get('view_name') or id != request.session.get('id')):
        return render(request, 'confirm_discard.html', {
            'form': DiscardSessionForm(),
            'view_name': request.session.get('view_name'),
            'id': request.session.get('id'),
        });

def get_player(name):
    """Returns a :class:`.models.Player` object. A new player will be created if the requested player doesn't exist.

    :param view_name: The name of the requested player.
    :type view_name: string.
    :returns: :class:`models.Player` -- The requested player.

    """
    try:
        player = Player.objects.get(name=name)
    except Player.DoesNotExist:
        player = Player(name=name)
        player.save()

    return player

def save_session(request):
    """Saves a track session. This function is called as soon as the player chooses to save his scores.

    :param request: The request object containing the user request.
    :type request: :class:`django.http.HttpRequest`.

    """
    if request.session.get('is_playing') and request.method == 'POST':
        form = SaveSessionForm(request.POST)

        if form.is_valid() and form.cleaned_data['save_session']:
            if request.session.get('drawing_id'):
                drawing = Drawing.objects.get(id=request.session.get('drawing_id'))
                player = get_player(form.cleaned_data['name'])

                drawing.player = player
                drawing.save()

            elif request.session.get('track_session_id'):
                track_session = TrackSession.objects.get(id=request.session.get('track_session_id'))
                player = get_player(form.cleaned_data['name'])

                track_session.player = player
                track_session.save()

                for drawing in Drawing.objects.filter(track_session=track_session):
                    drawing.player = player
                    drawing.save()

            clear_session(request)


def process_image(request, image):
    """Creates an edge image and calculates the values needed for the score calculation if necessary. This function is called as soon as an image is requested.

    :param request: The request object containing the user request.
    :type request: :class:`django.http.HttpRequest`.
    :param image: The image to be processed.
    :type image: :class:`models.Image`.

    """
    # detect edges
    if not image.edge_image:
        greyscale_image = io.imread(os.path.join(settings.MEDIA_ROOT, image.image.name), as_grey=True)

        # resize image
        height = len(greyscale_image)
        width = len(greyscale_image[0])
        factor = 768.0 / height
        greyscale_image = transform.resize(greyscale_image, [height * factor, width * factor])

        # detect edges
        edges = filter.canny(greyscale_image, sigma=image.canny_sigma, low_threshold=image.canny_low_threshold, high_threshold=image.canny_high_threshold)

        # save edge image
        temp_filename = '/tmp/' + request.session.session_key + '.png'
        io.imsave(temp_filename, ~edges * 1.)
        image.edge_image.save(slugify(os.path.splitext(os.path.basename(image.image.name))[0]) + '.png', File(open(temp_filename)))
        os.remove(temp_filename)

    if not image.dilated_edge_image:
        edge_image = io.imread(os.path.join(settings.MEDIA_ROOT, image.edge_image.name), as_grey=True)
        edge_image = edge_image.astype(np.float64)

        if edge_image.max() > 1.:
            edge_image /= 255.

        # map values greater .5 as edge
        edge_image = (1. - edge_image) / .5

        # save dilated edge image
        temp_filename = '/tmp/' + request.session.session_key + '.png'
        io.imsave(temp_filename, ~ndimage.binary_dilation(edge_image, iterations=2) * 1.)
        image.dilated_edge_image.save(slugify(os.path.splitext(os.path.basename(image.image.name))[0]) + '.png', File(open(temp_filename)))
        os.remove(temp_filename)

    # save maximum distance (needed for score calculation)
    if not image.max_distance:
        ones = np.ones(image.edge_image.height * image.edge_image.width).reshape((image.edge_image.height, image.edge_image.width))

        dilated_edge_image = io.imread(os.path.join(settings.MEDIA_ROOT, image.dilated_edge_image.name), as_grey=True)
        dilated_edge_image = dilated_edge_image.astype(np.float64)

        if dilated_edge_image.max() > 1.:
            dilated_edge_image /= 255.

        image.max_distance = np.sum(np.absolute(ones - dilated_edge_image))
        image.save()


def handle_finished_drawing(request):
    """This function is called as soon as the user finishes his drawing. It saves and associates his drawing to the running track session. It also assesses the score of the drawing.

    :param request: The request object containing the user request.
    :type request: :class:`django.http.HttpRequest`.
    :returns: :class:`models.Drawing` -- The created drawing object.

    """
    if request.session.get('is_playing'):
        if request.method == 'POST':
            form = FinishDrawingForm(request.POST)

            if form.is_valid() and form.cleaned_data['finish_drawing']:
                # save drawing
                image_data = base64.b64decode(request.POST['image'])
                temp_filename = '/tmp/' + request.session.session_key + '.png'
                file = open(temp_filename, 'wb')
                file.write(image_data)
                file.close()

                im = PImage.open(temp_filename)
                im = im.convert("RGB")
                im.save(temp_filename, "PNG")

                image = Image.objects.get(id=request.session.get('image_id'))

                # calculate distance
                greyscale_drawing = io.imread(temp_filename, as_grey=True)
                greyscale_drawing = misc.imresize(greyscale_drawing, (image.edge_image.height, image.edge_image.width), mode='F')
                dilated_edge_image = io.imread(os.path.join(settings.MEDIA_ROOT, image.dilated_edge_image.name), as_grey=True)

                greyscale_drawing = greyscale_drawing.astype(np.float64)
                dilated_edge_image = dilated_edge_image.astype(np.float64)

                # correct ranges of images if necessary
                if greyscale_drawing.max() > 1.:
                    greyscale_drawing /= 255.
                if dilated_edge_image.max() > 1.:
                    dilated_edge_image /= 255.

                missing_pixels = np.clip(greyscale_drawing - dilated_edge_image, 0., 1.)
                overlapping_pixels = np.clip((1. - greyscale_drawing) * (1. - dilated_edge_image), 0., 1.)
                superfluous_pixels = np.clip(dilated_edge_image - greyscale_drawing, 0., 1.)

                # number of pixels in the edge image which are not covered
                distance = np.sum(missing_pixels) * MISSING_PIXELS_PENALTY_FACTOR;
                # number of pixels in the drawing which are misplaced
                distance += np.sum(superfluous_pixels) * SUPERFLUOUS_PIXELS_PENALTY_FACTOR;
                score = max((image.max_distance - distance) / image.max_distance * 100, 0.)

                # save drawing
                drawing = Drawing(image=image, distance=distance, score=score)
                drawing.drawing.save(request.session.session_key + '.png', File(open(temp_filename)))

                # generate and save score image
                score_image = np.zeros((image.edge_image.height, image.edge_image.width, 3), dtype=np.float64)
                score_image[:, :, 0] += missing_pixels
                score_image[:, :, 1] += missing_pixels
                score_image[:, :, 2] += missing_pixels
                score_image[:, :, 0] += superfluous_pixels
                score_image[:, :, 1] += overlapping_pixels
                io.imsave(temp_filename, score_image * 1.)
                drawing.score_image.save(request.session.session_key + '_score.png', File(open(temp_filename)))

                drawing.save()

                # delete temporary file
                os.remove(temp_filename)

                return drawing
    return

def handle_finished_edge_image(request):
    """This function is called as soon as the admin finishes his drawing.

    :param request: The request object containing the user request.
    :type request: :class:`django.http.HttpRequest`.
    :returns: :class:`models.Drawing` -- The created drawing object.

    """
    if request.method == 'POST':
        form = FinishEdgeImageForm(request.POST)

        if form.is_valid() and form.cleaned_data['finish_edge_image']:
            # save new edge image
            image_data = base64.b64decode(request.POST['image'])
            temp_filename = '/tmp/' + request.session.session_key + '.png'
            file = open(temp_filename, 'wb')
            file.write(image_data)
            file.close()

            image = Image.objects.get(id=form.cleaned_data['image_id'])

            im = PImage.open(temp_filename)
            im = im.convert("RGB")
            im.save(temp_filename, "PNG")

            edge_image = io.imread(temp_filename, as_grey=True)
            edge_image = misc.imresize(edge_image, (image.edge_image.height, image.edge_image.width), mode='F')
            edge_image = edge_image.astype(np.float64)

            # correct ranges of images if necessary
            if edge_image.max() > 1.:
                edge_image /= 255.

            # save edge image
            image.edge_image.save(image.edge_image.name, File(open(temp_filename)))

            # delete old computed values
            image.max_distance = None
            image.dilated_edge_image.delete()
            image.save()

            # delete temporary file
            os.remove(temp_filename)

            return image.edge_image
    return

def handle_uploaded_file(request, form):
    """This function is called as soon as the user uploads a file. It saves his image on the filesystem.

    :param request: The request object containing the user request.
    :type request: :class:`django.http.HttpRequest`.
    :returns: :class:`models.Image` -- The created image object.

    """
    file = request.FILES['file']
    sigma = form.cleaned_data['sigma']

    # save file
    temp_filename = '/tmp/' + request.session.session_key
    with open(temp_filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    image = Image(title=slugify(file.name), canny_sigma=sigma)
    split = os.path.splitext(os.path.basename(file.name))
    image.image.save(slugify(split[0]) + split[1], File(open(temp_filename)))
    image.save()

    os.remove(temp_filename)

    return image

def handle_flickr_search(request, form):
    """This function is called as soon as the user submits a Flickr search query. It saves the found image on the filesystem.

    :param request: The request object containing the user request.
    :type request: :class:`django.http.HttpRequest`.
    :returns: :class:`models.Image` -- The created image object.

    """
    query = form.cleaned_data['query']
    sigma = form.cleaned_data['sigma']

    flickr = flickrapi.FlickrAPI(secret.FLICKR_API_KEY)
    for photo in flickr.walk(text=query, extras='1'):

        temp_filename = '/tmp/' + request.session.session_key + '.jpg'
        urllib.urlretrieve('http://farm' + photo.get('farm') + '.staticflickr.com/' + photo.get('server') + '/' + photo.get('id') + '_' + photo.get('secret') + '.jpg', temp_filename)

        title = slugify(str(photo.get('title')))
        image = Image(title=title, url='http://www.flickr.com/photos/' + photo.get('owner') + '/' + photo.get('id'), canny_sigma=sigma)
        image.image.save(title[:64] + '.jpg', File(open(temp_filename)))
        image.save()

        os.remove(temp_filename)

        return image


def index(request):
    """This is the view function for the home page.

    :param request: The request object containing the user request.
    :type request: :class:`django.http.HttpRequest`.
    :returns: :class:`django.http.HttpResponse` -- The rendered template as response.

    """
    clear_canvas = destroy_session(request)
    save_session(request)

    discard_session_page = check_session(request)
    if discard_session_page:
        return discard_session_page


    tracks = Track.objects.all()

    track_highscores = {}
    for track in tracks:
        track_highscores[track.id] = {
            'title': track.title,
            'highscores': TrackSession.objects.filter(player__isnull=False, track=track).order_by('-score'),
        }

    return render(request, 'main_menu.html', {
        'upload_file_form': UploadFileForm(),
        'search_flickr_form': SearchFlickrForm(),
        'tracks': tracks,
        'track_highscores': track_highscores,
        'single_drawing_highscores': Drawing.objects.filter(player__isnull=False, track_session__isnull=True),
        'clear_canvas': clear_canvas,
    })

def canvas(request, id=None):
    """This is the view function for a single drawing canvas. It is called for the file upload and Flickr game modes.

    :param request: The request object containing the user request.
    :type request: :class:`django.http.HttpRequest`.
    :param id: The id of the requested :class:`.models.Image`.
    :type id: int.
    :returns: :class:`django.http.HttpResponse` -- The rendered template as response.

    """
    view_name = 'Contour.contour.views.canvas'
    if id:
        id = long(id)
    elif view_name == request.session.get('view_name'):
        id = request.session.get('id')


    image = None;

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            image = handle_uploaded_file(request, form)
            if image:
                id = image.id

        form = SearchFlickrForm(request.POST)
        if form.is_valid():
            image = handle_flickr_search(request, form)
            if image:
                id = image.id


    if not image:
        try:
            image = Image.objects.get(id=id)
        except Image.DoesNotExist:
            raise Http404


    clear_canvas = destroy_session(request)

    discard_session_page = check_session(request, view_name, id)
    if discard_session_page:
        return discard_session_page

    if not request.session.get('is_playing'):
        request.session['image_id'] = id
        request.session['image_index'] = 0

    create_session(request, view_name, id)


    drawing = handle_finished_drawing(request)
    if drawing:
        request.session['last_drawing_id'] = drawing.id
        request.session['dont_show_welcome'] = True
        request.session['drawing_id'] = drawing.id
        request.session['image_index'] = request.session.get('image_index') + 1
        return HttpResponse(True)


    last_drawing = None
    if request.session.get('last_drawing_id'):
        try:
            last_drawing = Drawing.objects.get(id=request.session.get('last_drawing_id'))
        except Drawing.DoesNotExist:
            None


    if request.method == 'POST':
        form = RetryDrawingForm(request.POST)

        if form.is_valid() and form.cleaned_data['retry_drawing']:
            request.session['last_drawing_id'] = None
            request.session['image_index'] = request.session.get('image_index') - 1

            last_drawing.delete()
            last_drawing = None


    if request.session.get('image_index'):
        return render(request, 'completed.html', {
            'retry_drawing_form': RetryDrawingForm(),
            'save_session_form': SaveSessionForm(),
            'discard_session_form': DiscardSessionForm(),
            'drawing': Drawing.objects.get(id=request.session.get('drawing_id')),
            'last_drawing': last_drawing,
        })

    process_image(request, image)


    return render(request, 'game.html', {
        'finish_drawing_form': FinishDrawingForm(),
        'retry_drawing_form': RetryDrawingForm(),
        'image': image,
        'score': 0,
        'clear_canvas': clear_canvas,
        'show_welcome': not request.session.get('dont_show_welcome', False),
        'last_drawing': last_drawing,
    })

def track(request, id):
    """This is the view function for track sessions.

    :param request: The request object containing the user request.
    :type request: :class:`django.http.HttpRequest`.
    :param id: The id of the requested :class:`.models.Track`.
    :type id: int.
    :returns: :class:`django.http.HttpResponse` -- The rendered template as response.

    """
    view_name = 'Contour.contour.views.track'
    if id:
        id = long(id)

    try:
        track = Track.objects.get(id=id)
    except Track.DoesNotExist:
        raise Http404


    clear_canvas = destroy_session(request)

    discard_session_page = check_session(request, view_name, id)
    if discard_session_page:
        return discard_session_page

    if not request.session.get('is_playing'):
        track_session = TrackSession(session_key=request.session.session_key, track=track, score=0)
        track_session.save()

        request.session['image_index'] = 0
        request.session['track_session_id'] = track_session.id
    else:
        track_session = TrackSession.objects.get(id=request.session.get('track_session_id'))

    create_session(request, view_name, id)


    drawing = handle_finished_drawing(request)
    if drawing:
        drawing.track_session = track_session
        drawing.track_session_index = request.session.get('image_index')
        drawing.save()

        request.session['last_drawing_id'] = drawing.id
        request.session['dont_show_welcome'] = True
        request.session['image_index'] = request.session.get('image_index') + 1

        track_session.score += drawing.score
        track_session.save()
        return HttpResponse(True)


    last_drawing = None
    if request.session.get('last_drawing_id'):
        try:
            last_drawing = Drawing.objects.get(id=request.session.get('last_drawing_id'))
        except Drawing.DoesNotExist:
            None


    if request.method == 'POST':
        form = RetryDrawingForm(request.POST)

        if form.is_valid() and form.cleaned_data['retry_drawing']:
            request.session['last_drawing_id'] = None
            request.session['image_index'] = request.session.get('image_index') - 1

            track_session.score -= last_drawing.score
            track_session.save()

            last_drawing.delete()
            last_drawing = None


    try:
        image = TrackImage.objects.filter(track=track)[request.session.get('image_index')].image
    except IndexError:
        return render(request, 'completed.html', {
            'retry_drawing_form': RetryDrawingForm(),
            'save_session_form': SaveSessionForm(),
            'discard_session_form': DiscardSessionForm(),
            'track_session': track_session,
            'drawings': Drawing.objects.filter(track_session=track_session),
            'last_drawing': last_drawing,
        })

    request.session['image_id'] = image.id
    process_image(request, image)


    return render(request, 'game.html', {
        'finish_drawing_form': FinishDrawingForm(),
        'retry_drawing_form': RetryDrawingForm(),
        'image': image,
        'score': track_session.score,
        'clear_canvas': clear_canvas,
        'image_number': request.session.get('image_index') + 1,
        'image_count': TrackImage.objects.filter(track=track).count(),
        'show_welcome': not request.session.get('dont_show_welcome', False),
        'last_drawing': last_drawing,
    })

def drawing(request, id):
    """This is the view function to view the score summary of single drawings.

    :param request: The request object containing the user request.
    :type request: :class:`django.http.HttpRequest`.
    :param id: The id of the requested :class:`.models.Drawing`.
    :type id: int.
    :returns: :class:`django.http.HttpResponse` -- The rendered template as response.

    """
    if id:
        id = long(id)

    try:
        drawing = Drawing.objects.get(id=id, player__isnull=False)
    except Drawing.DoesNotExist:
        raise Http404

    return render(request, 'drawing.html', {
        'drawing': drawing,
    })

def session(request, id):
    """This is the view function to view the score summary of track sessions.

    :param request: The request object containing the user request.
    :type request: :class:`django.http.HttpRequest`.
    :param id: The id of the requested :class:`.models.TrackSession`.
    :type id: int.
    :returns: :class:`django.http.HttpResponse` -- The rendered template as response.

    """
    if id:
        id = long(id)

    try:
        track_session = TrackSession.objects.get(id=id, player__isnull=False)
    except TrackSession.DoesNotExist:
        raise Http404

    return render(request, 'session.html', {
        'track_session': track_session,
        'drawings': Drawing.objects.filter(track_session=track_session),
    })

def admin_edge_image(request, id):
    """This is the view function to edit the edge images in the admin section.

    :param request: The request object containing the user request.
    :type request: :class:`django.http.HttpRequest`.
    :param id: The id of the requested :class:`.models.Image`.
    :type id: int.
    :returns: :class:`django.http.HttpResponse` -- The rendered template as response.

    """
    if id:
        id = long(id)

    try:
        image = Image.objects.get(id=id)
    except Image.DoesNotExist:
        raise Http404

    process_image(request, image)

    edge_image = handle_finished_edge_image(request)
    if edge_image:
        return HttpResponse(True)

    return render(request, 'admin/edge_image.html', {
        'form': FinishEdgeImageForm(),
        'image': image,
    })
