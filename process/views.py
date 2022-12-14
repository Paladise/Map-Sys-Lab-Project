import base64
import logging
import secrets

from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from process.models import MapImage

log = logging.getLogger(__name__)

ID_LENGTH = 11

def base64_file(data, name=None):
    _format, _img_str = data.split(';base64,')
    _name, ext = _format.split('/')
    if not name:
        name = _name.split(":")[-1]
    return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext))


def index(request):
    return render(request, "home.html")


def atlas(request):
    if request.method == "POST":
        data = request.POST.dict()
        id = secrets.token_urlsafe(ID_LENGTH)
        for label, val in data.items():
            if label == "csrfmiddlewaretoken":
                continue            
            image = MapImage(id, label, base64_file(val, label))
            image.save()

        redirect_url = reverse("render:model", args=(id,))
        return redirect(redirect_url)

    return render(request, "atlas.html")
    
    
def temp(request):
    if request.method == "POST":
        id = secrets.token_urlsafe(ID_LENGTH)
        
        for filename, file in request.FILES.items():
            image = MapImage(id, filename, file)
            image.save()
        
        return JsonResponse({"id": id}, status=201)
    else:
        return render(request, "capture.html")