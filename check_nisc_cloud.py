#!/usr/bin/env python3
"""Check the status.cloud.coop site and return an overall status for the services based on embedded html status codes"""
import argparse, json, sys

try:
    import requests
    from lxml import html
except ImportError as ie:
    print(ie)
    sys.exit(3)

__author__ = "Rob Weber"
__email__ = "rweber@ecec.com"
__version__ = "1.0"

def getStatus():

    #full result, convert to json in the end
    result = {}

    #parse the html
    tree = html.fromstring(page.content)

    #get rows, skip the header
    rows = tree.xpath('/html/body/div[8]/div/table/tr[position() > 1]')

    for aRow in rows:
        #get the current status (returns list)
        status = aRow.xpath('td[1]/span')

        #split to get service:status pair
        splitString = status[0].get('title').split(':')

        result[splitString[0]] = splitString[1].lower()

    return result

try:
    #load the page
    page = requests.get('https://status.cloud.coop')
except Error:
    #if this fails we need to quit here
    print("status.cloud.coop could not be loaded")
    sys.exit(3) #unknown

#setup the cli parser
parser = argparse.ArgumentParser(description='check the status.cloud.coop site to see if the services are up, default is to check all services')
group = parser.add_mutually_exclusive_group()
group.add_argument('-j','--json',action='store_true',help='print the json formatted results')
group.add_argument('-s','--service',action='append',help='service to test for normal, can be more than one')

args = parser.parse_args()

#parse the html
services = getStatus()

if(args.json):
    #print out everything as json
    print(json.dumps(services))
    sys.exit(0)
else:
    checkServices = [] #services to check
    if(args.service):
        #check differences
        diff = list(set(args.service) - set(services.keys()))
        if(len(diff) > 0):
            print('The following service names are invalid %s' % diff)
            print('Valid services are: %s' % set(services.keys()))
            sys.exit(3)

        checkServices = args.service
    else:
        checkServices = services.keys()

    errors = []
    for service,status in services.items():
        #check the status of each service
        if(status == 'down' and service in checkServices):
            errors.append(service)
        elif(status == 'maintenance' and service in checkServices):
            #list maintenances for informational purposes
            print('%s is in maintenance' % service)

    if(len(errors) > 0):
        print('The following services are in an error state: %s' % errors)
        sys.exit(2)
    else:
        print('All NISC Cloud services are normal')
        sys.exit(0)
