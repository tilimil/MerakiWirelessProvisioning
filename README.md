# Meraki Wireless Site Provisioning

## Overview
This wireless site provisioning tool is meant to automate the provisioning of a Meraki wireless site, to include the following steps:
1.  Clone a template network with all of the requisite wireless settings and switch
2.  Add AP's and/or switches to the network
3.  Upload the floorplan/map
4.  Setup devices to include naming, tags, rf profile and floorplan/map placement


## Setup
1.  Copy config.json.default to config.json and input the variable for your site:
    * api_key - Meraki API key
    * org_id - Meraki organization ID
    * template_id - network ID of the template network
    * site_id - site number to be used in the ap naming convention
    * tags - tags that should be applied to the site in the meraki dashboard
    * timezone - timezone of the site you are Provisioning
    * network_name - name of the new Meraki network
    * img_file - floorplan image
    * anchor_lat - latitude of (0,0), bottom left corner of the building
    * anchor_long - longitude of (0,0), bottom left corner of the building
2.  Download [meraki.py](https://github.com/meraki/dashboard-api-python/blob/master/meraki.py) into the directory
3.  Put floorplan image into this directory
4.  Edit sample workseet.xlsx with your AP/switch device data.  Make sure that any rf_profile you use for AP's already exist in the template network.

## Usage
python3 ProvisionSite.py

## Automating Device location
This was designed for wireless site planning tools will set an anchor X/Y point as (0,0) on the map so that installers have a reference point to accurately place AP's down to the foot.
Because the Meraki floorplan API uses GPS coordinates (lat,long) to place devices, this script uses two inputs to automate device placement:
1.  GPS coordinates of X/Y (0,0) in feet - anchor_lat and anchor_long in config.json
2.  X/Y coordinates of the device from worksheet.xlsx

With this information, the function calcGPSOffset will derive the proper lat/long of the device for automatic placement onto the floorplan.