import base64
import pandas as pd
import cv2
import numpy as np
from base64 import b64encode
import json
import requests
import datetime
import time
import random
import numpy

#from PIL import Image
from io import BytesIO, StringIO
import re

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader
from django.core.files.storage import FileSystemStorage

from os import listdir
from os.path import isfile, join
import os


def index(request):
    template = loader.get_template('vaccination_checker/main.html')
    return HttpResponse(template.render())

@csrf_exempt
def image_selector(request):
    if request.method == "POST":
        print("Got file")
        base_html = request.POST['imageData']
        base = re.sub('^data:image/.+;base64,', '', base_html)

        imgdata123 = base64.b64decode(base)

        if not(os.path.exists('vaccination_checker/static/images/')):
                os.makedirs('vaccination_checker/static/images/')

        filename = 'vaccination_checker/static/images/'+datetime.datetime.fromtimestamp(time.time()).\
            strftime('%Y-%m-%d-%H-%M-%S')+'.jpg'
        with open(filename, 'wb') as f:
            f.write(imgdata123)
        #payload = {'success': True}
        #return HttpResponse(json.dumps(payload), content_type='application/json')

        onlyfiles = [f for f in listdir('vaccination_checker/static/images/') if isfile(join('vaccination_checker/static/images/', f))]
        files = []
        for file in onlyfiles:
            if(file.capitalize() != 'Thumbs.db'.capitalize()):
                files.append('images/' + file)
        template = loader.get_template('vaccination_checker/image_selector.html')
        context = {
            'imagedirectory': files
        }
        return HttpResponse(template.render(context))
    else:
        if not(os.path.exists('vaccination_checker/static/images/')):
                os.makedirs('vaccination_checker/static/images/')

        onlyfiles = [f for f in listdir('vaccination_checker/static/images/') if isfile(join('vaccination_checker/static/images/', f))]
        files = []
        for file in onlyfiles:
            if(file.capitalize() != 'Thumbs.db'.capitalize()):
                files.append('images/' + file)
        template = loader.get_template('vaccination_checker/image_selector.html')
        context = {
            'imagedirectory': files
        }
        return HttpResponse(template.render(context))

def worldmap(request):
    template = loader.get_template('vaccination_checker/worldmap.html')
    return HttpResponse(template.render())

import pickle

def summary(request):
    #ML Stuff

    if not(os.path.exists('vaccination_checker/static/images/')):
                os.makedirs('vaccination_checker/static/images/')
    onlyfiles = [f for f in listdir('vaccination_checker/static/images/') if
                 isfile(join('vaccination_checker/static/images/', f))]
    files = []
    newest_file = "vaccination_checker/static/images/1000-01-01-01-01-01.jpg"
    for file in onlyfiles:
            if(file.capitalize() != 'Thumbs.db'.capitalize()):
                files.append('vaccination_checker/static/images/' + file)
                if file < newest_file:
                    newest_file = 'vaccination_checker/static/images/' + file

    template = loader.get_template('vaccination_checker/summary.html')
    filename = newest_file
    # get all files
    o = {}
    for f in files:
        out = analyze(f)
        for key in out.keys():
            if key in o.keys():
                o[key] += out[key]
            else:
                o[key] = out[key]
    #info = vaccinationData[vaccinationData['Vaccination Name'].isin(out.keys())]
    print(out)
    print(files)
    out = o

    time_to_renewal = []
    message_doctor = []
    if out.keys().__len__() == 1:
        time_to_renewal = ['2 weeks']
        message_doctor = ['<a href=\'iMessage://01763954068\' class="btn btn-default btn-lg" role="button">Make an appointment with your doc</a>']
    elif out.keys().__len__() == 2:
        time_to_renewal = ['3 years', '2 weeks']
        message_doctor = ['','<a href=\'iMessage://01763954068\' class="btn btn-default btn-lg" role="button">Make an appointment with your doc</a>']
    elif out.keys().__len__() == 3:
        time_to_renewal = ['3 years', '2 weeks', '1 year']
        message_doctor = ['','<a href=\'iMessage://01763954068\' class="btn btn-default btn-lg" role="button">Make an appointment with your doc</a>','']
    elif out.keys().__len__() > 3:
        time_to_renewal = ['3 years', '2 weeks', '1 year']
        message_doctor = ['','<a href=\'iMessage://01763954068\' class="btn btn-default btn-lg" role="button">Make an appointment with your doc</a>','']
        for i in range(0,out.keys().__len__()-3):
            time_to_renewal.append(str(random.randint(2, 10)) + " years")
            message_doctor.append('')



    a = [(vac, vaccinationData[vaccinationData['Vaccination Name'] == vac]['Disease'].iloc[0], vaccinationData[vaccinationData['Vaccination Name'] == vac]['Amount of Shots (adults)'].iloc[0], out[vac], vaccinationData[vaccinationData['Vaccination Name'] == vac]['Output Information'].iloc[0]) for vac in out.keys()]
    i = 0
    b = []
    for element in a:
        element = list(element)
        element.append(time_to_renewal[i])
        element.append(message_doctor[i])
        if not(isinstance(element[2], str )) and numpy.isnan(element[2]):
            element[2] = "0 shots"
        if not(isinstance(element[4], str )) and numpy.isnan(element[4]):
            element[4] = ''

        b.append(element)
        i+=1
    a = b
    columns = ['Vaccine',
        'Disease',
          'Needed Shots',
          'Your Shots',
        'Additional information',
        'Time to vaccination expiry']
    df2 = pd.DataFrame(a)
    df2.columns = columns + ['msg']
    df2[columns].to_csv('vaccination_checker/static/export.csv')
    timestamp = time.strftime("%x, %H:%M:%S")
    #print(list(info.iterrows()))
    print(timestamp)
    context = {
        'row': a,
        'date' : timestamp
    }
    return HttpResponse(template.render(context))


####### LARI UND FREYAS PRETTY FUNCTIONS #####
vaccinationData = pickle.load(open('vaccination_checker/static/vaccinationInfo.p','rb'))
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

from difflib import SequenceMatcher


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def vaccinations_from_text(input_data):
    our_vaccinations = {}
    normalize = lambda x: ''.join((''.join(x.split(' '))).split('\n')).lower()
    for read_info in input_data:
        normalized_in = normalize(read_info)
        print(normalized_in)
        for vac in list(vaccinationData['Vaccination Name'].dropna().unique()):
            normalized_vac = normalize(vac)
            if similar(normalized_vac,normalized_in) > 0.9:
                print(normalized_in + '|' + normalized_vac)
            if similar(normalized_vac,normalized_in) > 0.9:
                if vac in our_vaccinations.keys():
                    our_vaccinations[vac] +=  1
                else:
                    our_vaccinations[vac] = 1
    return our_vaccinations

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
            text = [t['description'] for t in resp['textAnnotations']]
            return vaccinations_from_text(text[1:])
            for t in resp['textAnnotations']:
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

