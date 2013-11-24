import os
from django.shortcuts import render_to_response
from PIL import Image

def home(request):
    src_im = Image.open("winter3.jpg")
    return render_to_response('home/home.html')
