from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, welcome to the Vaccination Checker.")

def image_selector(request):
    return HttpResponse("Please upload your images.")

def summary(request):
    return HttpResponse("Here are your results.")