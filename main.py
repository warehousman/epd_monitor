 #  @filename   :   main.py
 #  @brief      :   epd cpu temperature monitor
 #  @author     :   warehousman
 #
 #  Copyright (C) warehousman     October 15 2018

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

COLORED = 1
UNCOLORED = 0

r=requests.get(endpoint, auth=HTTPBasicAuth(username, password))

def get_temp():
    if r.status_code == 200:
        returnDatas = {}
        xmldoc = parseString(r.text.encode('utf-8'))
        dataslist = xmldoc.getElementsByTagName('HardwareMonitorEntry')
        for s in dataslist:
            childs = s.childNodes
            key = slugify(childs[0].firstChild.nodeValue)
            returnDatas[key] = childs[5].firstChild.nodeValue

        return (returnDatas['gpu-temperature'])

def show():
    epd = epd1in54b.EPD()
    epd.init()

    # clear the frame buffer
    frame_black = [0xFF] * 5000
    frame_red = [0xFF] * 5000

# For simplicity, the arguments are explicit numerical coordinates
#    epd.draw_rectangle(frame_black, 10, 60, 50, 110, COLORED)
#    epd.draw_line(frame_black, 10, 60, 50, 110, COLORED)
#    epd.draw_line(frame_black, 50, 60, 10, 110, COLORED)
#    epd.draw_circle(frame_black, 120, 80, 30, COLORED)
#    epd.draw_filled_rectangle(frame_red, 10, 130, 50, 180, COLORED)
    epd.draw_filled_rectangle(frame_red, 10, 6, 190, 36, COLORED)
    epd.draw_filled_rectangle(frame_red, 10, 106, 190, 142, COLORED)
#    epd.draw_filled_circle(frame_red, 120, 150, 30, COLORED)

    # write strings to the buffer
    font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 28)
    epd.display_string_at(frame_black, 60, 60, get_temp(), font, COLORED)
    epd.display_string_at(frame_red, 28, 10, "GPU", font, UNCOLORED)
    epd.display_string_at(frame_red, 28, 110, "CPU", font, UNCOLORED)
    # display the frame
    epd.display_frame(frame_black, frame_red)

# display images
#    frame_black = epd.get_frame_buffer(Image.open('black.bmp'))
#    frame_red = epd.get_frame_buffer(Image.open('red.bmp'))
#    epd.display_frame(frame_black, frame_red)

    epd.sleep()

    # You can get frame buffer from an image or import the buffer directly:
    #epd.display_frame(imagedata.IMAGE_BLACK, imagedata.IMAGE_RED)

if __name__ == '__main__':
    show()
