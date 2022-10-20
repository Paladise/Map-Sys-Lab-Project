import base64
from django.core.files.base import ContentFile
from django.shortcuts import render
from process.models import MapImage


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
        for label, val in data.items():
            print(label, val)
            # image = MapImage(label = label, image = base64_file(val))
            # image.save()

    return render(request, "atlas.html")