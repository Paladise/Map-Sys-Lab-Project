import json
import logging
import os
import re
import subprocess

from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from heapq import heappush, heappop
from os import listdir

log = logging.getLogger(__name__)

MULTIPLIER = 2

def get_number_of_floors(id):
    result = subprocess.run(["ls", f"{settings.MEDIA_ROOT}maps/{id}"], capture_output = True, text = True)
    files = result.stdout.strip().split("\n")
    return sum(1 for file in files if file[:5] == "floor")
    
def index(request):
    # return render(request, "render.html")
    return render(request, "404.html", {"message": "imagine"})

def model(request, id):
    print("Calling model view")
    return render(request, "render_model.html", {"id": id})

def copy_images(request, id):
    print("Calling copy view")
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
    log.debug(f"Processing images view... with id {id}")
    requested_html = re.search(r'^text/html', request.META.get('HTTP_ACCEPT'))
    if not requested_html:
        result = subprocess.Popen(["ssh", f"2023abasto@hpc8.csl.tjhsst.edu", "bash",
                                  f"/cluster/2023abasto{settings.MEDIA_URL}{id}/process.sh"])
        
        current_time = datetime.now().strftime("%H:%M:%S")
        response_data = {"time": current_time}
        return JsonResponse(response_data, status=201)
    else:
        return render(request, "404.html", {"message": "Bad boy >:("})
        

def check_if_finished(request, id):
    log.debug(f"Check if finished view... with id {id}")
    
    num_floors = get_number_of_floors(id)
    current_time = datetime.now().strftime("%H:%M:%S")
    if os.path.isfile(f"{settings.MEDIA_ROOT}maps/{id}/render_floor1.json"):
        response_data = {"num_floors": num_floors}
        for i in range(1, num_floors + 1):
            log.debug(f"Check if finished view loading floor: {i}")
            
            with open(f"{settings.MEDIA_ROOT}maps/{id}/render_floor{i}.json", "r") as f:
                floor_data = json.load(f)
                
            response_data[str(i)] = floor_data 
        
        response_data["processed"] = "true"
        response_data["time"] = current_time
        
        with open(f"{settings.MEDIA_ROOT}maps/{id}/render_final.json", "w") as f:
            json.dump(response_data, f, indent = 4) 
    else:
        result = subprocess.run(["ssh", f"2023abasto@hpc8.csl.tjhsst.edu", "cd", 
                                f"/cluster/2023abasto{settings.MEDIA_URL}{id}", ";", "ls"],
            capture_output = True,
            text = True)
            
        files = result.stdout.strip().split("\n")
        
        log.debug(f"Check if finished view had files: {files}")
        
        log.debug(f"Check if finished view had # of floors: {num_floors}")
        
        if all(f"render_floor{i}.json" in files for i in range(1, num_floors + 1)):
            log.debug(f"Check if finished view had all floors")
            response_data = {"num_floors": num_floors}
            for i in range(1, num_floors + 1):
                copy_res = subprocess.run(["scp", f"2023abasto@hpc8.csl.tjhsst.edu:/cluster/2023abasto{settings.MEDIA_URL}/{id}/render_floor{i}.json",
                                          f"{settings.MEDIA_ROOT}maps/{id}/"])
                                          
                log.debug(f"Check if finished view copied floor: {i}")
                
                with open(f"{settings.MEDIA_ROOT}maps/{id}/render_floor{i}.json", "r") as f:
                    floor_data = json.load(f)
                    
                response_data[str(i)] = floor_data 
            
            response_data["processed"] = "true"
            response_data["time"] = current_time
        else:
            response_data = {"processed": "false", "time": current_time}
        
    log.debug(f"Check if finished view... should be returning JSON response now")
        
    return JsonResponse(response_data, status=201)
    
def pathfinding(request, id, x1, y1, x2, y2):
    start = (x1, y1)
    end = (x2, y2)
    response_data = {}
    with open(f"{settings.MEDIA_ROOT}maps/{id}/render_floor1.json") as f:
        data = json.load(f)

    map = data["map"]

    res = a_star(start, end, map)

    if res:
        path = [[(i[0] - 652) * MULTIPLIER, (380 - i[1]) * MULTIPLIER, 20] for i in res[2]]
        response_data["path"] = path

    return JsonResponse(response_data, status=201)

    
def a_star(start, end, map):
    log.debug("length")
    log.debug(len(map))
    log.debug(len(map[0]))
    closed = set()
    open = []
    start_node = (0, start, [])
    heappush(open, start_node)

    while open:
        node = heappop(open)
        coords, path = node[1], node[2]
        depth = len(path) + 1

        if coords[0] == end[0] and coords[1] == end[1]:
            return node
            
        for direction in ((-1, 0), (1, 0), (0, 1), (0, -1)):
            x1, y1 = direction
            new_coords = (coords[0] + x1, coords[1] + y1)
            if new_coords not in closed and map[new_coords[0]][new_coords[1]] == 0:
                closed.add(new_coords)
                child_node = (depth + heuristic(new_coords, path, end), new_coords, path + [new_coords])
                heappush(open, child_node)

    return None

def heuristic(new_coords, path, end):
    dx = abs(new_coords[0] - end[0])
    dy = abs(new_coords[1] - end[1])
    
    h = dx + dy
        
    return h * 1.000001
        
        