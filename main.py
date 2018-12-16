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
epd = epd1in54b.EPD()
epd.init()
key = os.environ.get('KEY')


def readtemp():
    url = "http://wareh.local/arduino/gettemp"
    response = requests.request("GET", url)
    data = response.json()
    return(data['temperature'])

def sendtemp():
    url = "https://thepopovs.herokuapp.com/api/temp"
    ts = datetime.datetime.now().timestamp()
    temp = readtemp()
    payload = json.dumps({'user_id': int(key),
                          'timestamp': 'ts',
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
    print(payload, response, temp)    

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
    except:
        pass
    return returnDatas

def epd_show_pc_stats():
    data = get_pc_stats()
# clear the frame buffer
    frame_black = [0xFF] * 5000
    frame_red = [0xFF] * 5000
# write strings to the buffer
    if 'gpu-temperature' in data:
        epd.display_string_at(frame_black, 60, 60, "C", font_b2, COLORED)
        epd.display_string_at(frame_black, 20, 60, str(data['gpu-temperature']), font_b, COLORED)
    if 'gpu-usage' in data:
        epd.display_string_at(frame_black, 170, 60, "%", font_b2, COLORED)
        epd.display_string_at(frame_black, 130, 60, str(data['gpu-usage']), font_b, COLORED)
    if 'cpu-temperature' in data:
        epd.display_string_at(frame_black, 60, 160, "C", font_b2, COLORED)
        epd.display_string_at(frame_black, 20, 160, str(data['cpu-temperature']), font_b, COLORED)
    if 'cpu-usage' in data:
        epd.display_string_at(frame_black, 170, 160, "%", font_b2, COLORED)
        epd.display_string_at(frame_black, 130, 160, str(data['cpu-usage']), font_b, COLORED)
# draw cells
    epd.draw_rectangle(frame_black, 5, 50, 100, 95, COLORED)
    epd.draw_rectangle(frame_black, 100, 50, 200, 95, COLORED)
    epd.draw_rectangle(frame_black, 5, 105, 100, 195, COLORED)
    epd.draw_rectangle(frame_black, 100, 150, 195, 195, COLORED)
# draw headers
    epd.draw_filled_rectangle(frame_black, 5, 5, 195, 50, COLORED)
    epd.draw_filled_rectangle(frame_black, 5, 105, 195, 150, COLORED)
    epd.display_string_at(frame_black, 28, 10, "GPU:", font_b, UNCOLORED)
    epd.display_string_at(frame_black, 28, 110, "CPU:", font_b, UNCOLORED)  
# display the frame
    epd.display_frame(frame_black, frame_red)

if __name__ == '__main__':
    print('Starting scheduler')
    logging.basicConfig()
    scheduler = BackgroundScheduler(timezone=utc)
    scheduler.add_job(sendtemp, 'interval', seconds=10)
    scheduler.start()
    try:
        while True:
            epd.init()
            epd_show_pc_stats()
            epd.sleep()
            time.sleep(15)    
    except (KeyboardInterrupt, SystemExit):
        print('Shutdown scheduler')
        scheduler.shutdown()