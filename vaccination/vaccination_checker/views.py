import json
import base64

from PIL import Image
from io import BytesIO, StringIO
import re

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader
from django.core.files.storage import FileSystemStorage


def index(request):
    template = loader.get_template('vaccination_checker/complete.html')
    return HttpResponse(template.render())

@csrf_exempt
def image_selector(request):
    if request.method == "POST":
        print("Got file")
        base_html = request.POST['imageData']
        base = re.sub('^data:image/.+;base64,', '', base_html)

        imgdata123 = base64.b64decode(base)
        filename = 'some_image.jpg'
        with open(filename, 'wb') as f:
            f.write(imgdata123)

        payload = {'success': True}
        #return HttpResponse(json.dumps(payload), content_type='application/json')
        template = loader.get_template('vaccination_checker/image_selector.html')
        return HttpResponse(template.render())
    else:
        template = loader.get_template('vaccination_checker/image_selector.html')
        return HttpResponse(template.render())

def summary(request):
    #ML Stuff
    template = loader.get_template('vaccination_checker/summary.html')
    return HttpResponse(template.render())

def worldmap(request):
    template = loader.get_template('vaccination_checker/worldmap.html')
    return HttpResponse(template.render())