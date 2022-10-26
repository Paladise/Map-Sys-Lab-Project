import json
import logging
import re
import subprocess

from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from os import listdir

log = logging.getLogger(__name__)

def get_number_of_floors(id):
    result = subprocess.run(["ls", f"{settings.MEDIA_ROOT}maps/{id}"], capture_output = True, text = True)
    files = result.stdout.strip().split("\n")
    return sum(1 for file in files if file[:5] == "floor")
    
def index(request):
    return render(request, "render.html")

def model(request, id):
    return render(request, "render_model.html", {"id": id})

def copy_images(request, id):
    requested_html = re.search(r'^text/html', request.META.get('HTTP_ACCEPT'))
    if not requested_html:
        subprocess.run(["ssh", "2023abasto@hpc8.csl.tjhsst.edu", "mkdir",
                       f"/cluster/2023abasto{settings.MEDIA_URL}{id}"])
        result = subprocess.run(["ls", f"{settings.MEDIA_ROOT}maps/{id}"], capture_output = True, text = True)
        
        files = result.stdout.strip().split("\n")
        
        for f in files:
            if "floor" not in f:
                continue
            copy_res = subprocess.run(["scp", f"{settings.MEDIA_ROOT}maps/{id}/{f}",
                                      f"2023abasto@hpc8.csl.tjhsst.edu:/cluster/2023abasto{settings.MEDIA_URL}{id}/"])
        
        current_time = datetime.now().strftime("%H:%M:%S")
        response_data = {"time": current_time}
        return JsonResponse(response_data, status=201)
    else:
        return render(request, "404.html", {"message": "Bad boy >:("})


def create_bash_script(request, id):
    requested_html = re.search(r'^text/html', request.META.get('HTTP_ACCEPT'))
    if not requested_html:
        files = listdir(f"{settings.MEDIA_ROOT}maps/{id}")
        with open(f'{settings.MEDIA_ROOT}maps/{id}/process.sh', 'w') as rsh:
            rsh.write('#!/bin/bash\n')
    
            for i, file in enumerate(files):
                if file[-3:] in ["jpg", "png"]:
                    rsh.write(f"python process_image.py {id} {file} &\n")
            
            if len(files) > 1:
                rsh.write("wait")
    
        copy_res = subprocess.run(["scp", f"{settings.MEDIA_ROOT}maps/{id}/process.sh",
                                  f"2023abasto@hpc8.csl.tjhsst.edu:/cluster/2023abasto{settings.MEDIA_URL}{id}/"])
    
        subprocess.run(["rm", f"{settings.MEDIA_ROOT}maps/{id}/process.sh"]) # Remove unnecessary process.sh file
    
        current_time = datetime.now().strftime("%H:%M:%S")
        response_data = {"time": current_time}
        return JsonResponse(response_data, status=201)
    else:
        return render(request, "404.html", {"message": "Bad boy >:("})
    
    
def process_images(request, id):
    requested_html = re.search(r'^text/html', request.META.get('HTTP_ACCEPT'))
    if not requested_html:
        log.debug(f"Processing images view... with id {id}")
        
        result = subprocess.Popen(["ssh", f"2023abasto@hpc8.csl.tjhsst.edu", "bash",
                                  f"/cluster/2023abasto{settings.MEDIA_URL}{id}/process.sh"])
        
        current_time = datetime.now().strftime("%H:%M:%S")
        response_data = {"time": current_time}
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
        
        current_time = datetime.now().strftime("%H:%M:%S")
        
        num_floors = get_number_of_floors(id)
        
        if all(f"render_floor{i}.json" in files for i in range(1, num_floors + 1)):
            response_data = {"num_floors": num_floors}
            for i in range(1, num_floors + 1):
                copy_res = subprocess.run(["scp", f"2023abasto@hpc8.csl.tjhsst.edu:/cluster/2023abasto{settings.MEDIA_URL}/{id}/render_floor{i}.json",
                                          f"{settings.MEDIA_ROOT}maps/{id}/"])
                
                with open(f"{settings.MEDIA_ROOT}maps/{id}/render_floor{i}.json", "r") as f:
                    floor_data = json.load(f)
                    
                response_data[str(i)] = floor_data 
            
            response_data["processed"] = "true"
            response_data["time"] = current_time
        else:
            response_data = {"processed": "false", "time": current_time}
            
        return JsonResponse(response_data, status=201)
    else:
        return render(request, "404.html", {"message": "Bad boy >:("})
        
        