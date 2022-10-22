import json
import subprocess

from os import listdir
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render


def index(request):
    return render(request, "render.html")

def model(request, id):
    return render(request, "render_model.html", {"id": id})

def copy_images(request, id):
    if request.method == "GET":
        print("Copying images...:")
        create_res = subprocess.run(["ssh", "2023abasto@hpc8.csl.tjhsst.edu", "mkdir", f"/cluster/2023abasto{settings.MEDIA_URL}{id}"])
        files = subprocess.run(["ls", f"{settings.MEDIA_ROOT}maps/{id}"], capture_output = True, text = True)
        
        files = [i.strip() for i in files.stdout.split("\n") if i]
        
        for f in files:
            copy_res = subprocess.run(["scp", f"{settings.MEDIA_ROOT}maps/{id}/{f}", f"2023abasto@hpc8.csl.tjhsst.edu:/cluster/2023abasto{settings.MEDIA_URL}{id}/"])
        
        response_data = {"files": str(files), "directory": " ".join(["ls", f"{settings.MEDIA_ROOT}maps/{id}"]), "create res": str(create_res), "copy res": str(copy_res)}
        return JsonResponse(response_data, status=201)
    else:
        return render(request, "404.html")

def create_bash_script(request, id):
    if request.method == "GET":
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
        return render(request, "404.html")
    
def process_images(request, id):
    if request.method == "GET":
        print("Processing images...:")
        result = subprocess.run(["ssh", f"2023abasto@hpc8.csl.tjhsst.edu", "bash", f"/cluster/2023abasto{settings.MEDIA_URL}{id}/process_images.sh"],
            capture_output = True,
            text = True)
        # print("Stdout:", result.stdout)
        if result.stderr:
            print("Stderr:\n", result.stderr)
        else:
            print("no errors")
        
        with open(f"{settings.MEDIA_ROOT}maps/{id}/render_floor1.json", "r") as f:
            response_data = json.load(f)
        return JsonResponse(response_data, status=201)
    else:
        return render(request, "404.html")
        
        