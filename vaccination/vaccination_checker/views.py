from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader


def index(request):
    template = loader.get_template('templates\\vaccination_checker\\test.html')
    return HttpResponse(template.render())

def image_selector(request):
    return HttpResponse("Please upload your images.")

def summary(request):
    return HttpResponse("Here are your results.")