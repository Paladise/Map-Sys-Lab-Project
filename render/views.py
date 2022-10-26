import json
import logging
import re
import subprocess

from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from os import listdir
from time import perf_counter

log = logging.getLogger(__name__)

def index(request):
    return render(request, "render.html")

def model(request, id):
    return render(request, "render_model.html", {"id": id})

def copy_images(request, id):
    requested_html = re.search(r'^text/html', request.META.get('HTTP_ACCEPT'))
    if not requested_html:
        create_res = subprocess.run(["ssh", "2023abasto@hpc8.csl.tjhsst.edu", "mkdir", f"/cluster/2023abasto{settings.MEDIA_URL}{id}"])
        files = subprocess.run(["ls", f"{settings.MEDIA_ROOT}maps/{id}"], capture_output = True, text = True)
        
        files = [i.strip() for i in files.stdout.split("\n") if i]
        
        for f in files:
            copy_res = subprocess.run(["scp", f"{settings.MEDIA_ROOT}maps/{id}/{f}", f"2023abasto@hpc8.csl.tjhsst.edu:/cluster/2023abasto{settings.MEDIA_URL}{id}/"])
        
        response_data = {"files": str(files), "directory": " ".join(["ls", f"{settings.MEDIA_ROOT}maps/{id}"]), "create res": str(create_res), "copy res": str(copy_res)}
        return JsonResponse(response_data, status=201)
    else:
        return render(request, "404.html", {"message": "Bad boy >:("})


def create_bash_script(request, id):
    requested_html = re.search(r'^text/html', request.META.get('HTTP_ACCEPT'))
    if not requested_html:
        files = listdir(f"{settings.MEDIA_ROOT}maps/{id}")
        with open(f'{settings.MEDIA_ROOT}maps/{id}/process_images.sh', 'w') as rsh:
            rsh.write('#!/bin/bash\n')
    
            for file in files:
                if file[-3:] in ["jpg", "png"]:
                    rsh.write(f'python process_image.py {id} {file}\n')
    
        copy_res = subprocess.run(["scp", f"{settings.MEDIA_ROOT}maps/{id}/process_images.sh", f"2023abasto@hpc8.csl.tjhsst.edu:/cluster/2023abasto{settings.MEDIA_URL}{id}/"])
    
        response_data = {"files": str(files), "copy": str(copy_res)}
        return JsonResponse(response_data, status=201)
    else:
        return render(request, "404.html", {"message": "Bad boy >:("})
    
    
def process_images(request, id):
    requested_html = re.search(r'^text/html', request.META.get('HTTP_ACCEPT'))
    if not requested_html:
        log.debug(f"Processing images view... with id {id}")
        start = perf_counter()
        # result = subprocess.run(["ssh", f"2023abasto@hpc8.csl.tjhsst.edu", "bash", f"/cluster/2023abasto{settings.MEDIA_URL}{id}/process_images.sh"],
        #     capture_output = True,
        #     text = True)
        
        # log.debug("Result stdout:\n" + result.stdout)
        
        result = subprocess.Popen(["ssh", f"2023abasto@hpc8.csl.tjhsst.edu", "bash", f"/cluster/2023abasto{settings.MEDIA_URL}{id}/process_images.sh"])
        
        with open(f"{settings.MEDIA_ROOT}maps/{id}/render_floor1.json", "r") as f:
            response_data = json.load(f)
            
        time_took = perf_counter() - start
        log.debug(f"View time took {time_took} seconds")
        return JsonResponse(response_data, status=201)
    else:
        return render(request, "404.html", {"message": "Bad boy >:("})
        

def check_if_finished(request, id):
    requested_html = re.search(r'^text/html', request.META.get('HTTP_ACCEPT'))
    if not requested_html:
        result = subprocess.run(["ssh", f"2023abasto@hpc8.csl.tjhsst.edu", "cd", 
                                f"/cluster/2023abasto{settings.MEDIA_URL}{id}", ";", "ls"],
            capture_output = True,
            text = True)
            
        files = result.stdout.strip().split("\n")
        
        if "render_floor1.json" in files:
            with open(f"{settings.MEDIA_ROOT}maps/{id}/render_floor1.json", "r") as f:
                response_data = json.load(f)
                response_data["processed"] = "true"
        else:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            response_data = {"processed": "false", "time": current_time}
            
        return JsonResponse(response_data, status=201)
    else:
        return render(request, "404.html", {"message": "Bad boy >:("})
        
        