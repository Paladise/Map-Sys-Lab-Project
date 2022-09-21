from django.shortcuts import render


def index(request):
    return render(request, "home.html")

def atlas(request):
    return render(request, "atlas.html")