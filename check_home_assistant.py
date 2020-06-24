#!/usr/bin/env python3
"""Can check the state of a Home Assistant entity. Use -h for arg descriptions"""
import requests
import json
import argparse
import sys

class HomeAssistant:
    url = None
    token = None

    def __init__(self, url, token):
        self.url = url
        self.token = token

    def _makeRequest(self, endpoint):
        headers = {
            'Authorization': 'Bearer %s' % self.token,
            'content-type': 'application/json',
        }

        response = requests.get('%s%s' % (self.url,endpoint), headers=headers)

        return json.loads(response.text)

    def getStates(self, entity = ''):
        return self._makeRequest('/api/states/%s' % entity)

    def getState(self, entity = ''):
        return self.getStates(entity)


def main():

    parser = argparse.ArgumentParser(description="Checks the status of a Home Assistant entity")
    parser.add_argument('-u', '--url', required=True,type=str, help='Home Assistant URL')
    parser.add_argument('-T', '--token', required=True, type=str, help='The long-lived access token for Home Assistant')
    parser.add_argument('-E', '--entity', required=True, type=str, help='The entity to check the status of')
    parser.add_argument('-c', '--critical', required=False, type=str, default='off', help='The critical state of the sensor, assumes "off" for a binary_sensor')
    parser.add_argument('-a', '--attribute', required=False, type=str, help='Attribute to display instead of the state')
    args = parser.parse_args(sys.argv[1:])

    h = HomeAssistant(args.url,args.token)

    aState = h.getState(args.entity)

    #display attribute, if set
    if(args.attribute is not None):
        print('%s' % aState['attributes'][args.attribute])
    else:
        print('%s: %s' % (aState['attributes']['friendly_name'], aState['state']))

    #figure out the exit condition
    if(aState['state'] == args.critical):
        exit(2)
    else:
        exit(0)

if __name__ == '__main__':
    main()
