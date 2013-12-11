import os
from django.shortcuts import render_to_response
from PIL import Image

def index(request):
    src_im = Image.open(os.path.join(os.getenv('OPENSHIFT_DATA_DIR'), "lenna.png"))
    return render_to_response('index.html', {"format": src_im.format})
