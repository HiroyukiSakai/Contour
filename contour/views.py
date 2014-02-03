import base64, os, pdb

from django.core.files import File
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template import RequestContext

import flickrapi, numpy as np
from scipy import ndimage
from skimage import data, filter, io, segmentation, transform

import secret
from .. import settings
from .forms import *
from .models import *
from .set_metrics import *


flickr = flickrapi.FlickrAPI(secret.FLICKR_API_KEY)
'''
for photo in flickr.walk(tag_mode='all',
        tags='sybren,365,threesixtyfive',
        min_taken_date='2008-08-20',
        max_taken_date='2008-08-30'):
    print photo.get('title')
'''

def create_session(request, view_name, id):
    if not request.session.get('is_playing'):
        request.session['is_playing'] = True
        request.session['view_name'] = view_name
        request.session['id'] = id

def destroy_session(request):
    if request.session.get('is_playing') and request.method == 'POST':
        form = DiscardSessionForm(request.POST)

        if form.is_valid() and form.cleaned_data['discard_session']:
            request.session['is_playing'] = False

def check_session(request, view_name=None, id=None):
    if request.session.get('is_playing') and (view_name != request.session.get('view_name') or id != request.session.get('id')):
        return render(request, 'confirm_discard.html', {
            'form': DiscardSessionForm(),
            'view_name': request.session.get('view_name'),
            'id': request.session.get('id'),
        });

def save_session(request):
    if request.session.get('is_playing') and request.method == 'POST':
        form = SaveSessionForm(request.POST)

        if form.is_valid() and form.cleaned_data['save_session']:
            track_session = TrackSession.objects.get(id=request.session.get('track_session_id'))

            try:
                player = Player.objects.get(name=form.cleaned_data['name'])
            except Player.DoesNotExist:
                player = Player(name=form.cleaned_data['name'])
                player.save()

            track_session.player = player
            track_session.save()

            for drawing in Drawing.objects.filter(track_session=track_session):
                drawing.player = player
                drawing.save()

            request.session['is_playing'] = False


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
        io.imsave(temp_filename, (1 - edges) * 255)
        image.edge_image.save(os.path.splitext(os.path.basename(image.image.name))[0] + '.png', File(open(temp_filename)))
        os.remove(temp_filename)

    # save maximum hausdorff distance (needed for score calculation)
    if not image.max_hausdorff_distance:
        zeros = np.zeros(image.edge_image.height * image.edge_image.width).reshape((image.edge_image.height, image.edge_image.width))
        edge_image = io.imread(os.path.join(settings.MEDIA_ROOT, image.edge_image.name), as_grey=True)
        image.max_hausdorff_distance = hausdorff_distance(1 - edge_image, zeros)
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
                greyscale_drawing = transform.resize(greyscale_drawing, [image.edge_image.height, image.edge_image.width])
                edge_image = io.imread(os.path.join(settings.MEDIA_ROOT, image.edge_image.name), as_grey=True)
                distance = hausdorff_distance(1 - greyscale_drawing, 1 - edge_image)
                score = (image.max_hausdorff_distance - distance) / image.max_hausdorff_distance * 100

                # save drawing
                drawing = Drawing(image=image, hausdorff_distance=distance, score=score)
                drawing.drawing.save(request.session.session_key + '.png', File(open(temp_filename)))
                drawing.save()

                # delete temporary file
                os.remove(temp_filename)

                return drawing
    return

def handle_uploaded_file(file, filename):
    with open('/home/Hiro/Contour/contour/media/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    image = io.imread('/home/Hiro/Contour/contour/media/' + filename, as_grey=True)
    edges = 1 - filter.canny(image, sigma=3)
    io.imsave('/home/Hiro/Contour/contour/media/' + filename, edges * 255)


def index(request):
    destroy_session(request)
    save_session(request)

    discard_session_page = check_session(request)
    if discard_session_page:
        return discard_session_page


    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            handle_uploaded_file(request.FILES['file'], request.FILES['file'].name)
            return render(request, 'game.html', {
                'image': request.FILES['file'].name,
            })


    return render(request, 'main_menu.html', {
        'form': UploadFileForm(),
        'tracks': Track.objects.all(),
    })

def track(request, id):
    view_name = 'Contour.contour.views.track'

    try:
        track = Track.objects.get(id=id)
    except Track.DoesNotExist:
        raise Http404


    destroy_session(request)

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
            'score': track_session.score
        })

    request.session['image_id'] = image.id
    process_image(request, image)


    return render(request, 'game.html', {
        'form': FinishDrawingForm(),
        'image': image,
        'score': track_session.score,
    })
