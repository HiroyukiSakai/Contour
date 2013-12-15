import os
from django.shortcuts import render_to_response

import numpy as np
from scipy import ndimage
from skimage import filter

# Generate noisy image of a square
'''
im = np.zeros((128, 128))
im[32:-32, 32:-32] = 1

im = ndimage.rotate(im, 15, mode='constant')
im = ndimage.gaussian_filter(im, 4)
im += 0.2 * np.random.random(im.shape)

# Compute the Canny filter for two values of sigma
edges1 = filter.canny(im)
edges2 = filter.canny(im, sigma=3)

# display results
plt.figure(figsize=(8, 3))

plt.subplot(131)
plt.imshow(im, cmap=plt.cm.jet)
plt.axis('off')
plt.title('noisy image', fontsize=20)

plt.subplot(132)
plt.imshow(edges1, cmap=plt.cm.gray)
plt.axis('off')
plt.title('Canny filter, $\sigma=1$', fontsize=20)

plt.subplot(133)
plt.imshow(edges2, cmap=plt.cm.gray)
plt.axis('off')
plt.title('Canny filter, $\sigma=3$', fontsize=20)

plt.subplots_adjust(wspace=0.02, hspace=0.02, top=0.9,
                    bottom=0.02, left=0.02, right=0.98)

plt.show()

def index(request):
    return render_to_response('index.html', {"format": src_im.format})
'''

def index(request):
     return render_to_response('index.html')
