import base64
import logging
import secrets

from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from process.models import MapImage, File

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
    
    
def capture(request):
    log.debug("Calling capture view")
    if request.method == 'POST':  
        file = request.FILES['file'].read()
        fileName= request.POST['filename']
        existingPath = request.POST['existingPath']
        end = request.POST['end']
        nextSlice = request.POST['nextSlice']
        id = request.POST['id']
        
        # log.debug(id)
        # log.debug(existingPath)
        # log.debug(fileName)
        # log.debug(end)
        # for f in File.objects.all():
        #     log.debug(f"F: {f.existingPath}, {f.name}, {f.eof}")

        if file=="" or fileName=="" or existingPath=="" or end=="" or nextSlice=="" or id =="":
            res = JsonResponse({'data':'Invalid Request'})
            return res
        else:
            if existingPath == 'null': 
                image = MapImage(id, "temp", request.FILES['file'])
                image.save()
                image.image.delete()

                path = f'media/maps/{id}/' + fileName
                with open(path, 'wb+') as destination: 
                    destination.write(file)
                FileFolder = File()
                FileFolder.existingPath = path
                FileFolder.eof = end
                FileFolder.name = fileName
                FileFolder.save()
                if int(end):
                    res = JsonResponse({'data':'Uploaded Successfully','existingPath': path})
                else:
                    res = JsonResponse({'existingPath': path})
                return res
            else:
                model_id = File.objects.get(existingPath=existingPath)
                if model_id.name == fileName:
                    if not model_id.eof:
                        with open(model_id.existingPath, 'ab+') as destination: 
                            destination.write(file)
                        if int(end):
                            model_id.eof = int(end)
                            model_id.save()
                            res = JsonResponse({'data':'Uploaded Successfully','existingPath':model_id.existingPath})
                        else:
                            res = JsonResponse({'existingPath':model_id.existingPath})    
                        return res
                    else:
                        res = JsonResponse({'data':'EOF found. Invalid request'})
                        return res
                else:
                    res = JsonResponse({'data':'No such file exists in the existingPath'})
                    return res
    else:
        return render(request, "capture.html")
    

def get_id(request):
    while True:
        id = secrets.token_urlsafe(ID_LENGTH)
        try:
            MapImage.objects.get(id=id)
        except MapImage.DoesNotExist:
            break
    return JsonResponse({"store_id": id})