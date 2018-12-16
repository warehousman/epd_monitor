#!/usr/bin/env python

import os
from pytz import utc
import datetime
import time
import requests
import json
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import math
import epd1in54b
from PIL import ImageFont
from requests.auth import HTTPBasicAuth
from xml.dom.minidom import parse, parseString
from slugify import slugify

username = "MSIAfterburner"
password = os.environ.get('ABPASS')
endpoint = os.environ.get("ABURL")
COLORED = 1
UNCOLORED = 0
font_b = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 32)
font_b2 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 24)
font_b3 = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 18)
epd = epd1in54b.EPD()
epd.init()
print("epd init")
key = os.environ.get('KEY')

def readtemp():
    data = {}
    try:
        url = "http://wareh.local/arduino/gettemp"
        response = requests.request("GET", url)
        data = response.json()
        return(data['temperature'])
    except:
        pass

def sendtemp():
    try:
        url = "https://thepopovs.herokuapp.com/api/temp"
        ts = datetime.datetime.now().isoformat()
        temp = readtemp()
        payload = json.dumps({'user_id': int(key),
                              'timestamp': ts,
                              'payload':{
                                 'percent': temp,
                                 'delta': 'amplitude'},
                              'type': 'amplitude'
                            })
        headers = {
        'Content-Type': "application/json",
        'cache-control': "no-cache",
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response, temp)
        return response.status_code    
    except:
        pass

def get_pc_stats():
    returnDatas = {}
    try:
        r=requests.get(endpoint, auth=HTTPBasicAuth(username, password))
        if r.status_code == 200:
            xmldoc = parseString(r.text.encode('utf-8'))
            dataslist = xmldoc.getElementsByTagName('HardwareMonitorEntry')
            for s in dataslist:
                childs = s.childNodes
                key = slugify(childs[0].firstChild.nodeValue)
                returnDatas[key] = math.trunc(float(childs[5].firstChild.nodeValue))
        return returnDatas
    except:
        pass

def epd_show_pc_stats():
    data = get_pc_stats()
    airtemp = readtemp()
# clear the frame buffer
    frame_black = [0xFF] * 5000
    frame_red = [0xFF] * 5000
# write strings to the buffer
    if 'gpu-temperature' in data:
        epd.display_string_at(frame_black, 60, 35, "C", font_b2, COLORED)
        epd.display_string_at(frame_black, 20, 35, str(data['gpu-temperature']), font_b, COLORED)
    if 'gpu-usage' in data:
        epd.display_string_at(frame_black, 170, 35, "%", font_b2, COLORED)
        epd.display_string_at(frame_black, 130, 35, str(data['gpu-usage']), font_b, COLORED)
    if 'cpu-temperature' in data:
        epd.display_string_at(frame_black, 60, 110, "C", font_b2, COLORED)
        epd.display_string_at(frame_black, 20, 110, str(data['cpu-temperature']), font_b, COLORED)
    if 'cpu-usage' in data:
        epd.display_string_at(frame_black, 170, 110, "%", font_b2, COLORED)
        epd.display_string_at(frame_black, 130, 110, str(data['cpu-usage']), font_b, COLORED)
    if airtemp:
        epd.display_string_at(frame_black, 90, 155, str(airtemp), font_b, COLORED)   
# draw cells
    epd.draw_rectangle(frame_black, 5, 25, 100, 75, COLORED)
    epd.draw_rectangle(frame_black, 100, 25, 195, 75, COLORED)
    epd.draw_rectangle(frame_black, 5, 100, 100, 150, COLORED)
    epd.draw_rectangle(frame_black, 100, 100, 195, 150, COLORED)
    epd.draw_rectangle(frame_black, 5, 150, 195, 195, COLORED)
# draw headers
    epd.draw_filled_rectangle(frame_black, 5, 5, 195, 30, COLORED)
    epd.draw_filled_rectangle(frame_black, 5, 75, 195, 100, COLORED)
    epd.display_string_at(frame_black, 28, 10, "GPU:", font_b3, UNCOLORED)
    epd.display_string_at(frame_black, 28, 80, "CPU:", font_b3, UNCOLORED)
    epd.display_string_at(frame_black, 28, 160, "AIR:", font_b2, COLORED)  
# display the frame
    epd.display_frame(frame_black, frame_red)

if __name__ == '__main__':
    print('Starting scheduler')
    logging.basicConfig()
    scheduler = BackgroundScheduler(timezone=utc)
    scheduler.add_job(sendtemp, 'interval', seconds=900)
    scheduler.start()
    print("Starting epd")
    try:
        while True:
            epd.init()
            epd_show_pc_stats()
            epd.sleep()
            time.sleep(30)    
    except (KeyboardInterrupt, SystemExit):
        print('Shutdown scheduler')
        scheduler.shutdown()