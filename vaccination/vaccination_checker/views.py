from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader


def index(request):
    template = loader.get_template('vaccination_checker/complete.html')
    return HttpResponse(template.render())

def image_selector(request):
    template = loader.get_template('vaccination_checker/image_selector.html')
    return HttpResponse(template.render())

def summary(request):
    #ML Stuff
    template = loader.get_template('vaccination_checker/summary.html')
    return HttpResponse(template.render())

def worldmap(request):
    template = loader.get_template('vaccination_checker/worldmap.html')
    return HttpResponse(template.render())