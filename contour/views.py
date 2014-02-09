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

import base64, os, pdb, urllib

from django.core.files import File
from django.http import Http404, HttpResponse
from django.shortcuts import render

import flickrapi, numpy as np
from scipy import misc
from skimage import filter, io, transform

import secret
from .. import settings
from .forms import *
from .models import *
from .set_metrics import *
from .util import _slugify


def create_session(request, view_name, id):
    if not request.session.get('is_playing'):
        request.session['is_playing'] = True
        request.session['view_name'] = view_name
        request.session['id'] = id

def clear_session(request):
    request.session['is_playing'] = False
    request.session['view_name'] = None
    request.session['id'] = None
    request.session['image_id'] = None
    request.session['image_index'] = None
    request.session['track_session_id'] = None
    request.session['drawing_id'] = None

def destroy_session(request):
    if request.session.get('is_playing') and request.method == 'POST':
        form = DiscardSessionForm(request.POST)

        if form.is_valid() and form.cleaned_data['discard_session']:
            clear_session(request)
            return True

    return

def check_session(request, view_name=None, id=None):
    if request.session.get('is_playing') and (view_name != request.session.get('view_name') or id != request.session.get('id')):
        return render(request, 'confirm_discard.html', {
            'form': DiscardSessionForm(),
            'view_name': request.session.get('view_name'),
            'id': request.session.get('id'),
        });

def get_player(name):
    try:
        player = Player.objects.get(name=name)
    except Player.DoesNotExist:
        player = Player(name=name)
        player.save()

    return player

def save_session(request):
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
        image.edge_image.save(_slugify(os.path.splitext(os.path.basename(image.image.name))[0]) + '.png', File(open(temp_filename)))
        os.remove(temp_filename)

    # save maximum hausdorff distance (needed for score calculation)
    if not image.max_hausdorff_distance:
        zeros = np.zeros(image.edge_image.height * image.edge_image.width).reshape((image.edge_image.height, image.edge_image.width))
        edge_image = io.imread(os.path.join(settings.MEDIA_ROOT, image.edge_image.name), as_grey=True)

        zeros = zeros.astype(np.float64)
        edge_image = edge_image.astype(np.float64)

        if edge_image.max() > 1.:
            edge_image /= 255.

        image.max_hausdorff_distance = hausdorff_distance(zeros, 1. - edge_image)
        image.save()


def handle_finished_drawing(request):
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

                image = Image.objects.get(id=request.session.get('image_id'))

                # calculate Hausdorff distance
                greyscale_drawing = io.imread(temp_filename, as_grey=True)
                greyscale_drawing = misc.imresize(greyscale_drawing, (image.edge_image.height, image.edge_image.width), mode='F')
                edge_image = io.imread(os.path.join(settings.MEDIA_ROOT, image.edge_image.name), as_grey=True)

                greyscale_drawing = greyscale_drawing.astype(np.float64)
                edge_image = edge_image.astype(np.float64)

                # correct ranges of images if necessary
                if greyscale_drawing.max() > 1.:
                    greyscale_drawing /= 255.
                if edge_image.max() > 1.:
                    edge_image /= 255.

                #io.imsave('/tmp/A.png', 1. - greyscale_drawing)
                #io.imsave('/tmp/B.png', 1. - edge_image)

                distance = hausdorff_distance(1. - greyscale_drawing, 1. - edge_image)
                score = (image.max_hausdorff_distance - distance) / image.max_hausdorff_distance * 100

                # save drawing
                drawing = Drawing(image=image, hausdorff_distance=distance, score=score)
                drawing.drawing.save(request.session.session_key + '.png', File(open(temp_filename)))
                drawing.save()

                # delete temporary file
                os.remove(temp_filename)

                return drawing
    return

def handle_uploaded_file(request, form):
    file = request.FILES['file']
    sigma = form.cleaned_data['sigma']

    # save file
    temp_filename = '/tmp/' + request.session.session_key
    with open(temp_filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    image = Image(title=_slugify(file.name), canny_sigma=sigma)
    split = os.path.splitext(os.path.basename(file.name))
    image.image.save(_slugify(split[0]) + split[1], File(open(temp_filename)))
    image.save()

    os.remove(temp_filename)

    return image

def handle_flickr_search(request, form):
    query = form.cleaned_data['query']
    sigma = form.cleaned_data['sigma']

    flickr = flickrapi.FlickrAPI(secret.FLICKR_API_KEY)
    for photo in flickr.walk(text=query, extras='1'):

        temp_filename = '/tmp/' + request.session.session_key + '.jpg'
        urllib.urlretrieve('http://farm' + photo.get('farm') + '.staticflickr.com/' + photo.get('server') + '/' + photo.get('id') + '_' + photo.get('secret') + '.jpg', temp_filename)

        title = _slugify(str(photo.get('title')))
        image = Image(title=title, url='http://www.flickr.com/photos/' + photo.get('owner') + '/' + photo.get('id'), canny_sigma=sigma)
        image.image.save(title[:64] + '.jpg', File(open(temp_filename)))
        image.save()

        os.remove(temp_filename)

        return image


def index(request):
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
        request.session['drawing_id'] = drawing.id
        request.session['image_index'] = request.session.get('image_index') + 1
        return HttpResponse(True)


    if request.session.get('image_index'):
        return render(request, 'completed.html', {
            'save_session_form': SaveSessionForm(),
            'discard_session_form': DiscardSessionForm(),
            'drawing': Drawing.objects.get(id=request.session.get('drawing_id')),
        })

    process_image(request, image)


    return render(request, 'game.html', {
        'form': FinishDrawingForm(),
        'image': image,
        'score': 0,
        'clear_canvas': clear_canvas,
    })

def track(request, id):
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

        request.session['image_index'] = request.session.get('image_index') + 1

        track_session.score += drawing.score
        track_session.save()
        return HttpResponse(True)


    try:
        image = TrackImage.objects.filter(track=track)[request.session.get('image_index')].image
    except IndexError:
        return render(request, 'completed.html', {
            'save_session_form': SaveSessionForm(),
            'discard_session_form': DiscardSessionForm(),
            'track_session': track_session,
            'drawings': Drawing.objects.filter(track_session=track_session),
        })

    request.session['image_id'] = image.id
    process_image(request, image)


    return render(request, 'game.html', {
        'form': FinishDrawingForm(),
        'image': image,
        'score': track_session.score,
        'clear_canvas': clear_canvas,
        'image_number': request.session.get('image_index') + 1,
        'image_count': TrackImage.objects.filter(track=track).count(),
    })

def drawing(request, id):
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
