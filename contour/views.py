from django.shortcuts import render_to_response

import flickrapi, numpy as np, secret
from scipy import ndimage
from skimage import data, filter, io, segmentation
from set_metrics import hausdorff_distance

flickr = flickrapi.FlickrAPI(secret.FLICKR_API_KEY)
'''
for photo in flickr.walk(tag_mode='all',
        tags='sybren,365,threesixtyfive',
        min_taken_date='2008-08-20',
        max_taken_date='2008-08-30'):
    print photo.get('title')
'''

# fileupload

# flickr
    # random or per search query

# Generate noisy image of a square
im = io.imread('/home/Hiro/Contour/contour/static/contour/img/lenna.tiff', as_grey=True)
im += 0.2 * np.random.random(im.shape)

# First trial with the Canny filter, with the default smoothing
edges = 1 - filter.canny(im, sigma=3)

io.imsave('/home/Hiro/Contour/contour/output.png', edges * 255)


# display image on canvas

# save canvas

# hausdorff distance

distance = hausdorff_distance(edges, edges)

# save image and high score

def index(request):
    return render_to_response('index.html', {
        'distance': distance
    })

def main_menu(request):
    return render_to_response('main_menu.html')

def game(request):
    return render_to_response('game.html')
