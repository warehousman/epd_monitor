import time
import math

import epd1in54b
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import requests
from requests.auth import HTTPBasicAuth
from xml.dom.minidom import parse, parseString
from slugify import slugify

username = "MSIAfterburner"
password = "17cc95b4017d496f82"
endpoint = "http://192.168.1.151:82/mahm"

COLORED = 1
UNCOLORED = 0

def get_stats():
    r=requests.get(endpoint, auth=HTTPBasicAuth(username, password))    
    if r.status_code == 200:
        returnDatas = {}
        xmldoc = parseString(r.text.encode('utf-8'))
        dataslist = xmldoc.getElementsByTagName('HardwareMonitorEntry')
        for s in dataslist:
            childs = s.childNodes
            key = slugify(childs[0].firstChild.nodeValue)
            returnDatas[key] = math.trunc(float(childs[5].firstChild.nodeValue))

        print (returnDatas)
    else:
        print (r)    

def main():
    epd = epd1in54b.EPD()
    epd.init()

    # clear the frame buffer
    frame_black = [0xFF] * (epd.width * epd.height / 8)
    frame_red = [0xFF] * (epd.width * epd.height / 8)

    # display images
    frame_black = epd.get_frame_buffer(Image.open('black.bmp'))
    frame_red = epd.get_frame_buffer(Image.open('red.bmp'))
    epd.display_frame(frame_black, frame_red)

    epd.sleep()

    # You can get frame buffer from an image or import the buffer directly:
    #epd.display_frame(imagedata.IMAGE_BLACK, imagedata.IMAGE_RED)

if __name__ == '__main__':
    while True:
        get_stats()
        main()
        time.sleep(2)
