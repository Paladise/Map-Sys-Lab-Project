import subprocess

from django.conf import settings
from django.shortcuts import render


def index(request):
    return render(request, "render.html")

def model(request, id):
    return render(request, "render_model.html", {"id": id})

def copy_images(request, id):
    if request.method == "GET":
        print("Copying images...:")
        files = subprocess.run(["ls", f"{settings.MEDIA_ROOT}maps\{id}"], capture_output = True, text = True, shell = True)
        print(files)
        files = "{" + ",".join([i.strip() for i in files.stdout.split("\n") if i]) + "}"

        subprocess.run(["cp", f"{settings.MEDIA_ROOT}maps\{id}\{files}", f"2023abasto@hpc8.csl.tjhsst.edu:/cluster/2023abasto{settings.MEDIA_URL}/{id}"])
        return {}