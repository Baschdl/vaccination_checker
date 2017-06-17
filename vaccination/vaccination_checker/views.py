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

        #decoded = base64.b64decode(fileReader)

        #file = open('image.png', 'w')
        #file.write(decoded)

        #im = Image.open(BytesIO(decoded))
        #im.save('accept.jpg', 'JPEG')

        base = re.sub('^data:image/.+;base64,', '', base_html)
        decoded = base64.b64decode(base)
        #image_data_str = image_data.decode("utf-8")
        image_data_str = str(decoded)
        #image = Image.open(StringIO(base))
        #image.save('accept.jpg', 'JPEG')

        #image_output = StringIO()
        #image_output.write(str(decoded))   # Write decoded image to buffer
        #image_output.seek(0)

        g = open("out.jpeg", "w")
        g.write(image_data_str)
        g.close()

        payload = {'success': True}
        return HttpResponse(json.dumps(payload), content_type='application/json')
    else:
        template = loader.get_template('vaccination_checker/image_selector.html')
        return HttpResponse(template.render())

def summary(request):
    return HttpResponse("Here are your results.")