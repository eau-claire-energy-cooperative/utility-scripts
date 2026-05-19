#!/usr/bin/env python3
"""
Check the status.cloud.coop site and return an overall status for the services using the REST API. Outages or Distruptions throw
a critical error (status code 2). https://status.cloud.coop/api/v1/services

Author: Rob Weber
Email: rweber@ecec.com
Version: 2.0

Usage:

# check all services
python3 check_nisc_cloud.py

# only check the SmartHub service
python3 check_nisc_cloud.py -s "SmartHub"

"""
import argparse, json, sys

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

# try to import requests - fail if not installed
try:
    import requests
except ImportError as ie:
    print(ie)
    sys.exit(UNKNOWN)

#setup the cli parser
parser = argparse.ArgumentParser(description='check the status.cloud.coop site to see if the services are up, default is to check all services')
group = parser.add_mutually_exclusive_group()
group.add_argument('-j','--json', action='store_true', help='print the json formatted results')
group.add_argument('-s','--service', action='append', help='service to test for normal, can be more than one')

args = parser.parse_args()

# try and load the status information
services = None
try:
    #load the page
    response = requests.get('https://status.cloud.coop/api/v1/services')
    response = json.loads(response.content)
except Error:
    #if this fails we need to quit here
    print("status.cloud.coop could not be loaded")
    sys.exit(UNKNOWN)

# format services as a map name: status
services = {}
for item in response['services']:
    state = item['status']

    if(state == 'incident'):
        # get the type of incident
        state = item['impact_level'].lower()

    # add name and status to the dict
    services[item['name']] = state

if(args.json):
    #print out everything as json
    print(json.dumps(services))
    sys.exit(OK)
else:
    checkServices = [] #services to check

    # if checking specific services
    if(args.service):
        # check if all service names are valid
        diff = list(set(args.service) - set(services.keys()))
        if(len(diff) > 0):
            print('The following service names are invalid %s' % diff)
            print('Valid services are: %s' % set(services.keys()))
            sys.exit(UNKNOWN)

        checkServices = args.service
    else:
        checkServices = services.keys()

    errors = []
    for service, status in services.items():
        #check the status of each service
        if(status in ['incident', 'outage', 'disruption'] and service in checkServices):
            errors.append(service)
        elif(status == 'maintenance' and service in checkServices):
            #list maintenances for informational purposes
            print('%s is in maintenance' % service)

    if(len(errors) > 0):
        print('The following services are in an outage state: %s' % errors)
        sys.exit(CRITICAL)
    else:
        print('All NISC Cloud services are normal')
        sys.exit(OK)
