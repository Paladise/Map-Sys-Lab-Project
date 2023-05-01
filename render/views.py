import json
import logging
import os
import re
import subprocess

from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from ast import literal_eval
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
            
            try:
                with open(f"{settings.MEDIA_ROOT}maps/{id}/render_floor{i}.json", "r") as f:
                    floor_data = json.load(f)
            except json.decoder.JSONDecodeError: # Didn't copy JSON file correctly, so removing it (will retry again)
                subprocess.run(["rm", f"{settings.MEDIA_ROOT}maps/{id}/render_floor{i}.json"])
                return JsonResponse({"Error": "Didn't copy JSON file correctly"}, status=201)
                
            response_data[str(i)] = floor_data 
            
            stair_coords.append([[int(j) for j in i] for i in floor_data["stairs"]])
        
        response_data["processed"] = "true"
        response_data["time"] = current_time
        log.debug(f"Found stairs: {len(stair_coords[0])}, {len(stair_coords[1])}")
        log.debug(f"Stairs: {stair_coords}")
        log.debug(f"Alignments: {len(find_alignments(stair_coords)[0].keys())}, {find_alignments(stair_coords)}")
        response_data["stairs"] = find_alignments(stair_coords)
        connect = sorted(response_data["stairs"][0].items())[0]
        log.debug([list(literal_eval(connect[0]))] + [list(i) for i in connect[1]])
        response_data["connect"] = [list(literal_eval(connect[0]))] + [list(i) for i in connect[1]]
        
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
                
                try:
                    with open(f"{settings.MEDIA_ROOT}maps/{id}/render_floor{i}.json", "r") as f:
                        floor_data = json.load(f)
                except json.decoder.JSONDecodeError: # Didn't copy JSON file correctly, so removing it (will retry again)
                    subprocess.run(["rm", f"{settings.MEDIA_ROOT}maps/{id}/render_floor{i}.json"])
                    return JsonResponse({"Error": "Didn't copy JSON file correctly"}, status=201)
                    
                response_data[str(i)] = floor_data 
                
                stair_coords.append([[int(j) for j in i] for i in floor_data["stairs"]])
            
            response_data["processed"] = "true"
            response_data["time"] = current_time
            response_data["stairs"] = find_alignments(stair_coords)
            connect = sorted(response_data["stairs"][0].items())[0]
            response_data["connect"] = [list(literal_eval(connect[0]))] + [list(i) for i in connect[1]]
            
            if "render_final.json" not in files:
                with open(f"{settings.MEDIA_ROOT}maps/{id}/render_final.json", "w") as f:
                    json.dump(response_data, f, indent = 4) 
        else:
            copied = [i for i in range(1, num_floors + 1) if f"render_floor{i}.json" in files]
            response_data = {"processed": "false", "time": current_time, "Finished floor(s)": copied}
        
    log.debug(f"Check if finished view... should be returning JSON response now")
        
    return JsonResponse(response_data, status=201)
    
def pathfinding(request, id, x1, y1, x2, y2, name1, name2, floor1, floor2):
    start = (x1, y1)
    end = (x2, y2)
    response_data = {}
    
    with open(f"{settings.MEDIA_ROOT}maps/{id}/render_final.json") as f:
        data = json.load(f)
        
    connect = data["connect"]
    
    log.debug(f"x1: {x1}, y1: {y1}, x2: {x2}, y2: {y2}, floor1: {floor1}, floor2: {floor2}")
    log.debug(f"connect: {connect}")
    
    if floor1 == floor2: # Rooms are on the same floor
    
        log.debug("Rooms are on the same floor")
            
        map = data[str(floor1)]["map"]
        doorways = data[str(floor1)]["doorways"]
        
        floor1 -= 1 # Subtract 1 since zero-indexed
        
        log.debug(doorways)
        log.debug(name1)
        log.debug(name2)
    
        res = a_star(start, end, map, doorways, name1, name2)
    
        if res:
            path = [[(i[0] - connect[floor1][0]) * MULTIPLIER, (connect[floor1][1] - i[1]) * MULTIPLIER, floor2] for i in res[2]]
            response_data["path"] = path
        else:
            response_data["ERROR"] = "Unable to find path"
            
    else: # Rooms are on different floors
    
            
        map1 = data[str(floor1)]["map"]
        doorways1 = data[str(floor1)]["doorways"]
        
        stair_coords = data["stairs"]
        
        floor1 -= 1 # Subtract 1 since zero-indexed
        
        stairs1 = {literal_eval(k): v for k, v in stair_coords[floor1].items()}
        
        # Go to nearest stairway
        
        dists = sorted(stairs1.items(), key = lambda k: (x1 - k[0][0])**2 + (y1 - k[0][1])**2) # Sort based on distance between stair and start
        
        log.debug(f"dists: {dists}")
        
        
        for stair_coord, stair_coord2 in dists:
            res1 = a_star(start, stair_coord, map1, doorways1, name1, "")
            
            if res1: # Break loop if found accessible stairway
                break
            
        if res1:
            # Transfer floors, and go to destination from second stairway
            
            map2 = data[str(floor2)]["map"]
            doorways2 = data[str(floor2)]["doorways"]
            
            floor2 -= 1
            
            stair_coord2 = tuple(stair_coord2[0]) # Temporary solution, will only work on 2 floors
            
            res2 = a_star(stair_coord2, end, map2, doorways2, "", name2)
            
            if res2:
                path = [[(i[0] - connect[floor1][0]) * MULTIPLIER, (connect[floor1][1] - i[1]) * MULTIPLIER, floor1 + 1] for i in res1[2]]
                path += [[(i[0] - connect[floor2][0]) * MULTIPLIER, (connect[floor2][1] - i[1]) * MULTIPLIER, floor2 + 1] for i in res2[2]]
                response_data["path"] = path
            else:
                response_data["ERROR"] = "Unable to find path"
    
    return JsonResponse(response_data, status=201)

    
def a_star(start, end, map, doorways, name1, name2):
    log.debug(f"called from A*, x_width: {len(map)} y_width: {len(map[0])}")
    
    start = tuple(start)
    end = tuple(end)
    
    doorways = {k: [tuple(i) for i in v] for k, v in doorways.items()}
    
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

        if coords == end or (name2 in doorways and coords in doorways[name2]):
            return node
            
        for direction in ((-1, 0), (1, 0), (0, 1), (0, -1)):
            x1, y1 = direction
            new_coords = (coords[0] + x1, coords[1] + y1)

            if new_coords[0] < 0 or new_coords[0] > x_width - 1 or new_coords[1] < 0 or new_coords[1] > y_width - 1:
                continue
            
            if new_coords not in closed and map[new_coords[0]][new_coords[1]] != 1:
                if map[new_coords[0]][new_coords[1]] == 2 and (name1 not in doorways or new_coords not in doorways[name1]) and (name2 not in doorways or new_coords not in doorways[name2]): # Non-passable doorway
                    continue
                closed.add(new_coords)
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
    def __init__(self, point, children=[], error=0.1):
        self.children = list() # Children are rest of stair points that are on the same floor
        self.point = tuple(point)
        self.error = error
        for child in children:
            self.children.append((self.point[0]-child[0], self.point[1]-child[1], tuple(child))) # Dist between point and child, and child
        self.children.sort(reverse=True) # Sort from smallest distance to greatest

    def add_children(self, child):
        self.children.append((self.point[0]-child[0], self.point[1]-child[1], tuple(child)))
        self.children.sort(reverse=True)

    def calc_ratio(self, x, y, x_dif, y_dif):
        return sqrt(x**2+y**2)/sqrt(x_dif**2+y_dif**2)

    def near(self, x_dif, y_dif):
        for x, y, n in self.children: # For every child (n) and distance between that point and child
            ratio = self.calc_ratio(x, y, x_dif, y_dif)
            
            x /= ratio
            y /= ratio
            low = ratio * (1 + self.error)
            high = ratio * (1 - self.error)
            if (float(x*low) <= x_dif <= float(x*high) or float(x*high) <= x_dif <= float(x*low)) and ((float(y*low) <= y_dif <= float(y*high)) or (float(y*high) <= y_dif <= float(y*low))):
                return n
        return None

    def align(self, target_points):
        matches = []
        for target_point in target_points: # For every target point
            match = [[self.point, target_point.point]]

            for x_dif, y_dif, p in target_point.children: # For every child (stair point on same floor) of the target point
                if self.near(x_dif, y_dif): # If that child is near to original point children
                    match.append([self.near(x_dif, y_dif), p]) # Append that original point child, and target point child
            matches.append(match) # Append that match to target point matches
        return matches

def assign_points(list1):
    """
    For each point in the list, create a stair point, with children being rest of stair points (on same floor)
    """
    toReturn = []
    for i in range(len(list1)):
        temp = list1.pop(0)
        toReturn.append(Stair_point(temp, list1))
        list1.append(temp)
    return toReturn

def create_dictionary(l1): # Create dictionary of best matches
    toReturn = []
    for i in range(len(l1[0])):
        toReturn.append(dict())
        
    for i in range(len(l1)):
        for j in range(len(l1[0])):
            toReturn[j][str(l1[i][j])] = list(l1[i])
            toReturn[j][str(l1[i][j])].remove(l1[i][j])
    return toReturn

def find_alignments(stair_points):
    x = assign_points(stair_points[0])
    y = assign_points(stair_points[1])
    best = (0, [])
    for i in range(len(x)): # For each stair point in first floor
        temp = x[i].align(y) # Try to create alignments
        for j in range(len(temp)): # For each alignment
            if len(temp[j]) > best[0]: # If there are more alignments than current best
                best = [len(temp[j]), (temp[j])] # Make current best those alignments
    return create_dictionary(best[1])