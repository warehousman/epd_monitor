 #  @filename   :   main.py
 #  @brief      :   epd cpu temperature monitor
 #  @author     :   warehousman
 #
 #  Copyright (C) warehousman     October 15 2018

import time
import epd1in54b
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
#import imagedata

import requests
from requests.auth import HTTPBasicAuth
from xml.dom.minidom import parse, parseString
from slugify import slugify

username = "MSIAfterburner"
password = "17cc95b4017d496f82"
endpoint = "http://192.168.1.151:82/mahm"

epd = epd1in54b.EPD()

COLORED = 1
UNCOLORED = 0

r=requests.get(endpoint, auth=HTTPBasicAuth(username, password))

def get_stats():
    if r.status_code == 200:
        returnDatas = {}
        xmldoc = parseString(r.text.encode('utf-8'))
        dataslist = xmldoc.getElementsByTagName('HardwareMonitorEntry')
        for s in dataslist:
            childs = s.childNodes
            key = slugify(childs[0].firstChild.nodeValue)
            returnDatas[key] = childs[5].firstChild.nodeValue

        return (returnDatas)

def show():
    epd.init()
    font_w = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 28)
    font_b = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 32)
    data = get_stats()

    # clear the frame buffer
    frame_black = [0xFF] * 5000
    frame_red = [0xFF] * 5000

    # draw headers
    epd.draw_filled_rectangle(frame_red, 10, 10, 190, 36, COLORED)
    epd.draw_filled_rectangle(frame_red, 10, 110, 190, 136, COLORED)
    epd.display_string_at(frame_red, 28, 10, "GPU", font_w, UNCOLORED)
    epd.display_string_at(frame_red, 28, 110, "CPU", font_w, UNCOLORED)

    # write strings to the buffer
    epd.display_string_at(frame_black, 20, 60, data['gpu-temperature'], font_b, COLORED)
    epd.display_string_at(frame_black, 110, 60, data['gpu-usage'], font_b, COLORED)
    epd.display_string_at(frame_black, 20, 160, data['cpu-temperature'], font_b, COLORED)
    epd.display_string_at(frame_black, 110, 160, data['cpu-usage'], font_b, COLORED)
    # display the frame
    epd.display_frame(frame_black, frame_red)

    epd.sleep()

if __name__ == '__main__':
    while True:
        show()
        time.sleep(10)