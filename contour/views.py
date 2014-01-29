from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

import flickrapi, numpy as np
from scipy import ndimage
from skimage import data, filter, io, segmentation

import secret
from .forms import UploadFileForm
from .set_metrics import hausdorff_distance


def handle_uploaded_file(file, filename):
    with open('/home/Hiro/Contour/contour/media/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

    image = io.imread('/home/Hiro/Contour/contour/media/' + filename, as_grey=True)
    edges = 1 - filter.canny(image, sigma=3)
    io.imsave('/home/Hiro/Contour/contour/media/' + filename, edges * 255)

    distance = hausdorff_distance(edges, edges)


flickr = flickrapi.FlickrAPI(secret.FLICKR_API_KEY)
'''
for photo in flickr.walk(tag_mode='all',
        tags='sybren,365,threesixtyfive',
        min_taken_date='2008-08-20',
        max_taken_date='2008-08-30'):
    print photo.get('title')
'''


# display image on canvas

# save canvas

# hausdorff distance

# save image and high score

def main_menu(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'], request.FILES['file'].name)
            return render_to_response('game.html', {
                'image': request.FILES['file'].name,
            }, context_instance=RequestContext(request))
    else:
        form = UploadFileForm()
    return render_to_response('main_menu.html', {
        'form': form,
    }, context_instance=RequestContext(request))

def game(request):
    return render_to_response('game.html')
