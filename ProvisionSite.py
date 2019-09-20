import meraki
import pprint
import json
import re
import sys
import requests
import pandas as pd
import math
import base64
import time
import logging
#logging.basicConfig(level=logging.DEBUG)

with open('config.json') as json_file:
    config = json.load(json_file)

ORG_ID = config['org_id']
API_KEY = config['api_key']
TEMPLATE_ID =  config['template_id']
SITE_ID = config['site_id']
TAGS = config['tags']
TIMEZONE = config['timezone']
NETWORK_NAME = config['network_name']
IMG_FILE = config['img_file']
ANCHOR_LAT = config['anchor_lat']
ANCHOR_LONG = config['anchor_long']

def makeAPName(site_id, apnum):
    if int(apnum) < 10:
            apstring = str('00') + str(apnum)
    if int(apnum) >= 10 and apnum < 100:
            apstring = str('0') + str(apnum)
    if int(apnum) >= 100:
            apstring = str(apnum)
    apname = 'APUS-' + str(site_id) + '-' + str(apstring)
    return apname

def getDeviceDetailFromMac(macstring, inventory):
    #macstring must be formatted like 11:22:33:44:55:66
    for device in inventory:
        if macstring in device['mac']:
            return device
    return False

def createFloorPlan(image_file, apikey, networkid, latitude, longitude):  
    with open(image_file, "rb") as file:
        image_base64 = base64.b64encode(file.read())

    base_url = 'https://api.meraki.com/api/v0'
    posturl = '{0}/networks/{1}/floorPlans'.format(
        str(base_url), str(networkid))
    
    headers = {
        'x-cisco-meraki-api-key': format(str(apikey)),
        'Content-Type': 'application/json'
    }

    postdata = {
        "name" : NETWORK_NAME,
        "center": {
                "lat": latitude,
                "lng": longitude
                },
        "imageContents": image_base64.decode('utf-8')
    }

    postdata = json.dumps(postdata)
    dashboard = requests.post(posturl, data=postdata, headers=headers, timeout=4)
    counter = 0
    while dashboard.status_code != 201 and counter < 5:
        #print(dashboard.status_code)
        #print(dashboard.text)
        print('Error uploading floorplan trying again')
        dashboard = requests.post(posturl, data=postdata, headers=headers, timeout=4)
        counter += 1

    return json.loads(dashboard.text)

def deleteFloorPlan(apikey, networkid, floorid):
    base_url = 'https://api.meraki.com/api/v0'
    deleteurl = '{0}/networks/{1}/floorPlans/{2}'.format(
        str(base_url), str(networkid), str(floorid))

    headers = {
        'x-cisco-meraki-api-key': format(str(apikey)),
        'Content-Type': 'application/json'
    }

    dashboard = requests.delete(deleteurl, headers=headers)
    print(dashboard.text)
    return True

def listFloorPlans(apikey, networkid):
    base_url = 'https://api.meraki.com/api/v0'
    geturl = '{0}/networks/{1}/floorPlans'.format(
        str(base_url), str(networkid))

    headers = {
        'x-cisco-meraki-api-key': format(str(apikey)),
        'Content-Type': 'application/json'
    }

    dashboard = requests.get(geturl, headers=headers)
    print(dashboard.text)
    return True

def listOrgs(apikey):
    base_url = 'https://api.meraki.com/api/v0/organizations'

    headers = {
        'x-cisco-meraki-api-key': format(str(apikey)),
        'Content-Type': 'application/json'
    }

    dashboard = requests.get(base_url, headers=headers)
    print(dashboard.text)
    return True

def listNetworks(apikey, orgid):
    base_url = 'https://api.meraki.com/api/v0'
    geturl = '{0}/organizations/{1}/networks'.format(
        str(base_url), str(orgid))

    headers = {
        'x-cisco-meraki-api-key': format(str(apikey)),
        'Content-Type': 'application/json'
    }

    dashboard = requests.get(geturl, headers=headers)
    print(dashboard.text)
    return True

def listRFProfiles(apikey, networkid):
    base_url = 'https://api.meraki.com/api/v0'
    geturl = '{0}/networks/{1}/wireless/rfProfiles'.format(
        str(base_url), str(networkid))

    headers = {
        'x-cisco-meraki-api-key': format(str(apikey)),
        'Content-Type': 'application/json'
    }

    dashboard = requests.get(geturl, headers=headers)
    print(dashboard.text)
    return True
    

def updateDeviceLocation (apikey, networkid, serial, aplat, aplong, floorid):
    base_url = 'https://api.meraki.com/api/v0'
    posturl = '{0}/networks/{1}/devices/{2}'.format(
        str(base_url), str(networkid), str(serial))
    
    headers = {
        'x-cisco-meraki-api-key': format(str(apikey)),
        'Content-Type': 'application/json'
    }

    postdata = {
        "floorPlanId" : floorid,
        "lat": aplat,
        "lng": aplong,
    }

    postdata = json.dumps(postdata)
    dashboard = requests.put(posturl, data=postdata, headers=headers)
    return True

def listRFProfiles(apikey, networkid):
    base_url = 'https://api.meraki.com/api/v0'
    geturl = '{0}/networks/{1}/wireless/rfProfiles'.format(
        str(base_url), str(networkid))

    headers = {
        'x-cisco-meraki-api-key': format(str(apikey)),
        'Content-Type': 'application/json'
    }

    dashboard = requests.get(geturl, headers=headers)
    return json.loads(dashboard.text)

def updateRFProfile(apikey, networkid, serial, rfprofileid):
    base_url = 'https://api.meraki.com/api/v0'
    posturl = '{0}/networks/{1}/devices/{2}/wireless/radioSettings'.format(
        str(base_url), str(networkid), str(serial))
    
    headers = {
        'x-cisco-meraki-api-key': format(str(apikey)),
        'Content-Type': 'application/json'
    }
    postdata = {"rfProfileId" : str(rfprofileid)}

    postdata = json.dumps(postdata)
    dashboard = requests.put(posturl, data=postdata, headers=headers)
    return True 

def calcGPSOffset( anchorlat, anchorlong, xoffset, yoffset):
    #convert feet to meters for conversion formula
    xoffset = xoffset / 3.28084
    yoffset = yoffset / 3.28084
    pi = 3.14159265359
    newlong = anchorlong + (180/pi) * (xoffset/6378137) / math.cos(anchorlat * (pi/180))
    newlat = anchorlat + (180/pi) * (yoffset/6378137)
    return newlat, newlong

def main():
    inventory = meraki.getorginventory(API_KEY, ORG_ID, suppressprint=True)
    xls = pd.ExcelFile('worksheet.xlsx')
    df = xls.parse(xls.sheet_names[0])
    devicedict = df.to_dict()

    for item in ['Device Type', 'Name', 'MAC or Serial', 'Tags', 'RF Profile', 'X', 'Y']:
        if item not in devicedict:
            print("No column named " + item + ". Exiting...")
            exit()

    ## make sure all the devices are in the organization and not claimed elsewhere
    print("Checking inventory in spreadsheet for availability in Meraki dashboard")
    for id in devicedict['Name']:
        if devicedict['Device Type'][id] == 'AP':
            device = getDeviceDetailFromMac(devicedict['MAC or Serial'][id].lower(), inventory)
            if device:
                pass
            else:
                print("AP with mac address " + str(devicedict['MAC or Serial'][id]) + " does not exist in this organization")
                exit()
            if device['networkId'] is not None:
                print("AP with mac address " + str(devicedict['MAC or Serial'][id]) + " is already added to another network")
                exit()

    print("Creating network for store " + NETWORK_NAME)
    result = meraki.addnetwork(API_KEY, ORG_ID, NETWORK_NAME, 'wireless switch', TAGS, TIMEZONE, TEMPLATE_ID, suppressprint=True)
    newnet_id = result['id']
    print("Created network id " + newnet_id)

    print("Uploading floorplan")
    floorplandata = createFloorPlan(IMG_FILE, API_KEY, newnet_id, ANCHOR_LAT, ANCHOR_LONG)
    FLOOR_ID = floorplandata['floorPlanId']
    input("Please scale the map in the Meraki dashboard and then hit enter to continue...")

    rfprofiledata = listRFProfiles(API_KEY, newnet_id)
    rfprofilelookup = {}
    for rfprofile in rfprofiledata:
        rfprofilelookup[rfprofile['name']] = rfprofile['id']

    print("Naming devices, applying tags, applying RF profile and inserting devices onto floorplan")
    for id in devicedict['Name']:
        if devicedict['Device Type'][id] == 'AP':
            serialnum = getDeviceDetailFromMac(devicedict['MAC or Serial'][id].lower(), inventory)['serial']
            devicename = makeAPName(SITE_ID, devicedict['Name'][id])
            devicetags = devicedict['Tags'][id].split(",")
            
        if devicedict['Device Type'][id] == 'Switch':
            serialnum = devicedict['MAC or Serial'][id]
            devicename = devicedict['Name'][id]
            devicetags = devicedict['Tags'][id].split(",")

        result = meraki.adddevtonet(API_KEY, newnet_id, serialnum, suppressprint=True)
        result = meraki.updatedevice(API_KEY, newnet_id, str(serialnum), name=devicename, tags=devicetags, lat=ANCHOR_LAT, lng=ANCHOR_LONG, suppressprint=True)
        DEVICE_LAT, DEVICE_LONG = calcGPSOffset( ANCHOR_LAT,  ANCHOR_LONG, devicedict['X'][id], devicedict['Y'][id] )
        updateDeviceLocation(API_KEY, newnet_id, serialnum, DEVICE_LAT, DEVICE_LONG, FLOOR_ID)

        if devicedict['Device Type'][id] == 'AP':
            updateRFProfile(API_KEY, newnet_id, serialnum, rfprofilelookup[devicedict['RF Profile'][id]])
    
    print("Site provisioning complete")

if __name__ == "__main__":
    main()
