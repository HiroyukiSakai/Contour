from django.shortcuts import render_to_response

def index(request):
    return render_to_response('index.html')

def main_menu(request):
    return render_to_response('main_menu.html')

def game(request):
    return render_to_response('game.html')
