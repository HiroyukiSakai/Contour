import os, Image
from django.shortcuts import render_to_response

def index(request):
    src_im = Image.open(os.path.join(os.getenv('OPENSHIFT_DATA_DIR'), "lenna.png"))
    return render_to_response('index.html')
