import pandas as pd
import numpy as np

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib import rc, font_manager

from bidi.algorithm import get_display
import arabic_reshaper
from matplotlib import cm
from PIL import Image, ImageFont, ImageDraw

import os
import socket

import requests
from io import BytesIO

import jdatetime

from collections import OrderedDict


def rtl_fix(name):
    # some magic happens here and makes RTL fixed
    # for writing correct text on image!
    reshaped_name = arabic_reshaper.reshape(name)
    return get_display(reshaped_name)


def calculate_pos(*args):
    # do your position calculation
    return (args[0], args[1])

def types(types_):
    dict_ = {1: "سرخوش",
             2: "فیلسوف",
             3: "شاهزاده",
             4: "جنگجو",
             5: "کاریزماتیک",
             6: "رومانتیک",
        }
    return dict_.get(types_, 'None')

def generate_plot(req):
    font = {#'family' : 'arial'
            #,'weight' : 'bold'
            'size'   : 9
        }

    rc('font', **font)

    url = 'static/shabnam-fd.ttf'
    prop = font_manager.FontProperties(fname=url)

    value1 = rtl_fix("چهره")
    value2 = rtl_fix("هوش")
    value3 = rtl_fix("مهر")
    value4 = rtl_fix("قابل‌اعتماد")
    value5 = rtl_fix("شجاعت")
    value6 = rtl_fix("اندام")
    value7 = rtl_fix("اعتمادبنفس")
    value8 = rtl_fix("اجتماعی")
    value9 = rtl_fix("متفکر")
    value10 = rtl_fix("تاثیرگذاری")

    d = OrderedDict()

    d[value1] = req['data'][0]
    d[value2] = req['data'][1]
    d[value3] = req['data'][2]
    d[value4] = req['data'][3]
    d[value5] = req['data'][4]
    d[value6] = req['data'][5]
    d[value7] = req['data'][6]
    d[value8] = req['data'][7]
    d[value9] = req['data'][8]
    d[value10] = req['data'][9]


    json = {
        "data": d,
        "firstname": req['firstname'],
        "lastname": req['lastname'],
        "voters": req['voters'],
        "score": req['score'],
        "pic": req['pic'],
        "type": req['type']
    }

    df = pd.DataFrame(list(json["data"].items()), columns=['name', 'value'])

    color = cm.viridis(np.linspace(.4,.7, 10))

    my_colors = 'rgbkymcrgb'

    ax = df.plot(kind='bar', legend=False, figsize=(8.6, 3), color=[color], stacked=True, width = 0.8)
    for p in ax.patches:
        ax.annotate(str(int(p.get_height())), (p.get_x() + p.get_width() / 2., p.get_height()), fontsize='x-large', ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontproperties=prop)
    for i, x in enumerate(df.name):
        ax.text(i+0.1, -0.8, x, fontsize='x-large', ha='right', rotation=60, fontproperties=prop)
    ax.grid(False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.axison=False
    ax.set_ylim(0,10)

    fig = ax.get_figure()
    fig.savefig('static/plot.png', transparent=True, bbox_inches = 'tight')


    background = Image.open('static/960903.jpg').convert("RGBA")

    # User's picture
    if json['pic'] != 'empty':
        response = requests.get(json['pic'])
        user_image = Image.open(BytesIO(response.content)).convert("RGBA")
        background.paste(user_image, (600, 50), user_image)
        #bg_image = Image.open("bg.png").convert("RGBA")
        #background.paste(bg_image, (0, 0), bg_image)

    # User's name
    name_font = ImageFont.truetype('static/acme.ttf', 90)
    draw = ImageDraw.Draw(background)
    w1, h = draw.textsize(json['firstname'],font=name_font)
    draw.text((565-w1, 120),json['firstname'],(0,0,0),font=name_font)
    if json['lastname'] != 'empty':
        w2, h = draw.textsize(json['lastname'],font=name_font)
        draw.text((565-w2, 200),json['lastname'],(255,255,255),font=name_font)

    # Last update time
    small_font = ImageFont.truetype('static/acme.ttf', 25)
    time_ = "Last update: " + jdatetime.date.today().strftime("%Y-%m-%d")
    draw.text((265, 325),time_,(0,0,0),font=small_font)

    # Your Score
    num_font = ImageFont.truetype('static/acme.ttf', 100)
    w, h = draw.textsize(str(json['score']),font=num_font)
    draw.text((((240-w)/2)+160, 490),str(json['score']),(0,0,0),font=num_font)

    # Count of voters
    num_font = ImageFont.truetype('static/acme.ttf', 55)
    w, h = draw.textsize(str(json['voters']),font=num_font)
    draw.text((((90-w)/2)+60, 450),str(json['voters']),(255,255,255),font=num_font)

    # Your symbol
    symbol = types(json['type'])
    num_font = ImageFont.truetype('static/shabnam.ttf', 60)
    w, h = draw.textsize(rtl_fix(symbol),font=num_font)
    draw.text((((330-w)/2)+560, 505),rtl_fix(symbol),(0,0,0),font=num_font)
    symbol_image = Image.open('static/' + str(json['type']) + '.png').convert("RGBA")
    background.paste(symbol_image, (500, 455), symbol_image)

    # The graph
    foreground = Image.open('static/plot.png').convert("RGBA")
    background.paste(foreground, (235, 640), foreground)

    background = background.convert("RGB")
    background.save('static/tmp' +str(req['data_id'])+ '.jpg')

    HOSTNAME = socket.gethostname()
    
    final_url = 'static/tmp' +str(req['data_id'])+ '.jpg'
    return final_url

