import requests
import json
import time

def readtemp():
    data = {}
    try:
        url = "http://wareh.local/arduino/gettemp"
        response = requests.request("GET", url)
        data = response.json()
#       if response.status_code
        print(response.status_code)
        return response.status_code
    except:
        pass
    return(response)

if __name__ == '__main__':
    t = readtemp()
    print(t)