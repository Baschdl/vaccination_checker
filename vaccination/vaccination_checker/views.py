import base64
import pandas as pd
import cv2
import numpy as np
from base64 import b64encode
import json
import requests

#from PIL import Image
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
        analyze(filename)
        payload = {'success': True}
        return HttpResponse(json.dumps(payload), content_type='application/json')
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

####### LARI UND FREYAS PRETTY FUNCTIONS #####

ENDPOINT_URL = 'https://vision.googleapis.com/v1/images:annotate'
RESULTS_DIR = 'jsons'
API_KEY = 'AIzaSyCv-h5VNRepCR9dlXTMsLZ6gN0a-_FnWJM'

def make_image_data_list(image_filenames):
    """
    image_filenames is a list of filename strings
    Returns a list of dicts formatted as the Vision API
        needs them to be
    """
    img_requests = []
    for imgname in image_filenames:
        with open(imgname, 'rb') as f:
            ctxt = b64encode(f.read()).decode()
            img_requests.append({
                    'image': {'content': ctxt},
                    'features': [{
                        'type': 'TEXT_DETECTION',
                        'maxResults': 1
                    }]
            })
    return img_requests

def make_image_data(image_filenames):
    """Returns the image data lists as bytes"""
    imgdict = make_image_data_list(image_filenames)
    return json.dumps({"requests": imgdict }).encode()


def request_ocr(api_key, image_filenames):
    response = requests.post(ENDPOINT_URL,
                             data=make_image_data(image_filenames),
                             params={'key': api_key},
                             headers={'Content-Type': 'application/json'})
    return response


def draw_intersection(lines,img):
    vertical = []
    horizontal = []
    line_count = len(lines)
    for l in lines:
        temp_img = np.zeros(img.shape, np.uint8)
        rho = l[0][0]
        theta = l[0][1]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))

        if 0.1 > a and -0.1 < a:
            #horizontal
            horizontal += [((x1, y1), (x2, y2))]
            cv2.line(temp_img, (x1, y1), (x2, y2), (20, 0,0), 2)
        else:
            #vertical
            vertical += [((x1, y1), (x2, y2))]
            cv2.line(temp_img, (x1, y1), (x2, y2), (0, 0,20), 2)
        #cv2.imwrite('x'+a+'.jpg',temp_img)
        img = img +  temp_img
    return img


def cut_image(file):
    img = cv2.imread(file)
    origin = img.copy()
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    width, height, channels = img.shape
    # create houghline
    edges = cv2.Canny(gray,50,150,apertureSize = 3)
    cv2.imwrite('b.jpg',edges)
    lines = cv2.HoughLines(edges,rho=1,theta=np.pi/180,threshold=270)

    line_img = np.zeros((width,height,3), np.uint8)
    line_img = draw_intersection(lines,line_img)
    #dilate
    dil_kernel = np.ones((8,8), np.uint8)
    line_img = cv2.dilate(line_img,dil_kernel,iterations=1)
    line_img = cv2.erode(line_img,dil_kernel,iterations=1)
    b,g,r = cv2.split(line_img)
    conv = lambda x: 254 if x != 0 else 1
    conv2 = np.vectorize(conv)
    g2 = np.zeros(b.shape,np.uint8) + np.all([b > 0,r > 0],axis=0).astype(np.uint8)
    g3 = conv2(g2)
    g3 = g3.astype(np.uint8)

    line_img = cv2.merge((b,g,r))
    line_img = cv2.merge((np.zeros(b.shape,np.uint8),g3,np.zeros(b.shape,np.uint8)))
    dil_kernel = np.ones((10,10), np.uint8)
    line_img = cv2.dilate(line_img,dil_kernel,iterations=1)
    line_img = cv2.erode(line_img,dil_kernel,iterations=1)
    ret,thresh = cv2.threshold(cv2.cvtColor(line_img,cv2.COLOR_BGR2GRAY),10,255,0)
    image, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    centroids = []
    xs = []
    ys = []
    for c in contours:
        M = cv2.moments(c)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        centroids += [(cX,cY)]
        xs += [cX]
        ys += [cY]
    xS = pd.Series(xs)
    yS = pd.Series(ys)
    x1 = xS.min()
    x2 = xS[xS > xS.min() +width/10].min()
    y1 = yS.min()
    return origin[y1:,x1:x2,:]

def analyze(file):
    img = cut_image(file)
    temp_file = 'temp.jpg'
    cv2.imwrite(temp_file, img)
    image_filenames = [temp_file]
    response = request_ocr(API_KEY, image_filenames)
    if response.status_code != 200 or response.json().get('error'):
        print(response.text)
    else:
        for idx, resp in enumerate(response.json()['responses']):
            # save to JSON file
            imgname = image_filenames[idx]
            # print the plaintext to screen for convenience
            for t in resp['textAnnotations']:
                print(t['description'])
                des = ''.join(''.join(t['description'].lower().split(' ')).split('\n'))
                if 'cervarix' in des \
                        or 'menjugate' in des \
                        or 'havrix' in des \
                        or 'rabipur' in des \
                        or 'ixiaro' in des:
                    print("---------------------------------------------")
                    print("    Bounding Polygon:")
                    xs = []
                    ys = []
                    for d in t['boundingPoly']['vertices']:
                        xs += [d['x']]
                        ys += [d['y']]
                    xS = pd.Series(xs)
                    yS = pd.Series(ys)
                    print("    Text:")
                    print(t['description'])
                    cv2.rectangle(img, (xS.min(), yS.min()), (xS.max(), yS.max()), (0, 255, 0), thickness=3, lineType=8,
                                  shift=0)
    cv2.imwrite('aaaa.jpg', img)