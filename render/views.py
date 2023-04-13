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
from math import sqrt
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
    log.debug("Calling model view")
    return render(request, "render.html", {"id": id})

def copy_images(request, id):
    log.debug("Calling copy view")
    requested_html = re.search(r'^text/html', request.META.get('HTTP_ACCEPT'))
    if not requested_html:
        subprocess.run(["ssh", "2023abasto@hpc8.csl.tjhsst.edu", "mkdir",
                       f"/cluster/2023abasto{settings.MEDIA_URL}{id}"])
        result = subprocess.run(["ls", f"{settings.MEDIA_ROOT}maps/{id}"], capture_output = True, text = True)
        
        files = result.stdout.strip().split("\n")
        
        for f in files:
            if "floor" not in f and "symbol" not in f:
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
                if file[-3:] in ["jpg", "png"] and not file.startswith("symbol"):
                    rsh.write(f"python process.py {id} {file} &\n")
            
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
        stair_coords = []
        for i in range(1, num_floors + 1):
            log.debug(f"Check if finished view loading floor: {i}")
            
            with open(f"{settings.MEDIA_ROOT}maps/{id}/render_floor{i}.json", "r") as f:
                floor_data = json.load(f)
                
            response_data[str(i)] = floor_data 
            
            stair_coords.append(floor_data["stairs"])
        
        response_data["processed"] = "true"
        response_data["time"] = current_time
        response_data["stairs"] = find_alignments(stair_coords)
        
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
            stair_coords = []
            for i in range(1, num_floors + 1):
                copy_res = subprocess.run(["scp", f"2023abasto@hpc8.csl.tjhsst.edu:/cluster/2023abasto{settings.MEDIA_URL}/{id}/render_floor{i}.json",
                                          f"{settings.MEDIA_ROOT}maps/{id}/"])
                                          
                log.debug(f"Check if finished view copied floor: {i}")
                
                with open(f"{settings.MEDIA_ROOT}maps/{id}/render_floor{i}.json", "r") as f:
                    floor_data = json.load(f)
                    
                response_data[str(i)] = floor_data 
                
                stair_coords.append(floor_data["stairs"])
            
            response_data["processed"] = "true"
            response_data["time"] = current_time
            response_data["stairs"] = find_alignments(stair_coords)
        else:
            response_data = {"processed": "false", "time": current_time}
        
    log.debug(f"Check if finished view... should be returning JSON response now")
        
    return JsonResponse(response_data, status=201)
    
def pathfinding(request, id, x1, y1, x2, y2, name1, name2, floor1, floor2):
    start = (x1, y1)
    end = (x2, y2)
    response_data = {}
    
    if floor1 == floor2: # Rooms are on the same floor
    
        with open(f"{settings.MEDIA_ROOT}maps/{id}/render_floor{floor1}.json") as f:
            data = json.load(f)
    
        map = data["map"]
        doorways = data["doorways"]
        
        log.debug(doorways)
        log.debug(name1)
        log.debug(name2)
    
        res = a_star(start, end, map, doorways, name1, name2)
    
        if res:
            path = [[(i[0] - 652) * MULTIPLIER, (380 - i[1]) * MULTIPLIER, 1] for i in res[2]] # HARDCODED
            response_data["path"] = path
        else:
            response_data["ERROR"] = "Unable to find path"
            
    else:
        with open(f"{settings.MEDIA_ROOT}maps/{id}/render_floor{floor1}.json") as f:
            data1 = json.load(f)
    
        with open(f"{settings.MEDIA_ROOT}maps/{id}/render_floor{floor2}.json") as f:
            data2 = json.load(f)
            
        map1 = data["map"]
        doorways1 = data["doorways"]
        
        # Go to nearest stairway
        
        # Transfer floors
        
        # Repeat to destination
    
    return JsonResponse(response_data, status=201)

    
def a_star(start, end, map, doorways, name1, name2):
    log.debug(f"called from A*, x_width: {len(map)} y_width: {len(map[0])}")
    
    closed = set()
    open = []
    start_node = (0, start, [])
    heappush(open, start_node)
    
    x_width = len(map)
    y_width = len(map[0])

    while open:
        node = heappop(open)
        coords, path = node[1], node[2]
        depth = len(path) + 1
        
        # log.debug(f"looking at node {coords}: {map[coords[0]][coords[1]]}, open: {len(open)}")

        if coords[0] == end[0] and coords[1] == end[1]:
            return node
            
        for direction in ((-1, 0), (1, 0), (0, 1), (0, -1)):
            x1, y1 = direction
            new_coords = [coords[0] + x1, coords[1] + y1]

            if new_coords[0] < 0 or new_coords[0] > x_width - 1 or new_coords[1] < 0 or new_coords[1] > y_width - 1:
                continue
            
            if tuple(new_coords) not in closed and map[new_coords[0]][new_coords[1]] != 1:
                if map[new_coords[0]][new_coords[1]] == 2 and (name1 in doorways and new_coords not in doorways[name1]) and (name2 in doorways and new_coords not in doorways[name2]): # Non-passable doorway
                    continue
                closed.add(tuple(new_coords))
                child_node = (depth + heuristic(new_coords, path, end), new_coords, path + [new_coords])
                heappush(open, child_node)

    return None

def heuristic(new_coords, path, end):
    dx = abs(new_coords[0] - end[0])
    dy = abs(new_coords[1] - end[1])
    
    h = dx + dy
        
    return h
    
##############################################
# Stair calculations
##############################################

class Stair_point():
    def __init__(self, point, children=[], error=.05):
        self.children = list()
        self.point = tuple(point)
        self.error = error
        for child in children:
            self.children.append((self.point[0]-child[0], self.point[1]-child[1], tuple(child)))
        self.children.sort(reverse=True)

    def add_children(self, child):
        self.children.append((self.point[0]-child[0], self.point[1]-child[1], tuple(child)))
        self.children.sort(reverse=True)

    def calc_ratio(self, x, y, x_dif, y_dif):
        return sqrt(x**2+y**2)/sqrt(x_dif**2+y_dif**2)

    def near(self, x_dif, y_dif):
        for x, y, n in self.children:
            temp = (sqrt(x**2+y**2)/sqrt(x_dif**2+y_dif**2))
            x = x/temp
            y = y/temp
            low = temp*(1+self.error)
            high = temp*(1-self.error)
            if (float(x*high) <= x_dif <= float(x*low)) and ((float(y*low) <= y_dif <= float(y*high)) or (float(y*high) <= y_dif <= float(y*low))):
                return n
        return None

    def align(self, target_points):
        matches = []
        for point in target_points:
            match = [[self.point, point.point]]

            for x_dif, y_dif, p in point.children:
                if self.near(x_dif, y_dif):
                    match.append([self.near(x_dif, y_dif), p])
            matches.append(match)
        return matches

def average(x1, x2, y1, y2):
    return ((x1+x2)/2, (y1+y2)/2)

def average_list(list1):
    toReturn = []
    for point in list1:
        toReturn.append(average(point[0], point[1], point[2], point[3]))
    return toReturn

def asign_points(list1):
    toReturn = []
    for i in range(len(list1)):
        temp = list1.pop(0)
        toReturn.append(Stair_point(temp, list1))
        list1.append(temp)
    return toReturn

def compare(l1, l2):
    toReturn = []
    for ele in l1:
        if ele not in l2:
            toReturn.append(ele)
    return toReturn

def create_dictionary(l1):
    toReturn = []
    for i in range(len(l1[0])):
        toReturn.append(dict())
    for i in range(len(l1)):
        for j in range(len(l1[0])):
            toReturn[j][l1[i][j]] = list(l1[i])
            toReturn[j][l1[i][j]].remove(l1[i][j])
    return toReturn

def find_alignments(stair_points):
    n = 1
    x = asign_points(stair_points[0])
    y = asign_points(stair_points[1])
    best = (0, [])
    highs = []
    for i in range(len(x)):
        temp = x[i].align(y)
        for j in range(len(temp)):
            if len(temp[j]) > best[0]:
                best = [len(temp[j]), (temp[j])]
    return create_dictionary(best[1])