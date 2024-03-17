from django.http import HttpResponse
from django.shortcuts import render
import folium
from django.views.decorators.clickjacking import xframe_options_exempt
import pandas as pd
from django.http import JsonResponse
from folium.plugins import MarkerCluster
import subprocess
import os

def index(request):
    city_name = request.GET.get('city', "Chozeau")
    origin_cd = os.getcwd()
    os.chdir("website_immo")
    subprocess.run(["python", "FoliumMap.py", city_name, '5', 'Appartement'])
    os.chdir(origin_cd)
    return render(request, r"templates\index.html", context={})


@xframe_options_exempt
def map_immo(request):
    return render(request, r"templates\map.html", context={})



