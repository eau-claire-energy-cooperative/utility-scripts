#!/usr/bin/env python
"""check various components of a Cradlepoint IBR600 device"""
import argparse
import json
import sys
import requests
from requests.auth import HTTPDigestAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

#disable insecure request warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class HttpGetter:
    address = ''
    secret = ''
    
    def __init__(self,host,port,password):
        self.address = 'https://%s:%i/api/' % (host,port)
        self.secret = password
        
    def getAddress(self):
        return self.address

    def getAuth(self):
        return HTTPDigestAuth("admin", self.secret)

    def findVZWInfo(self,json):
        radios = json['data']['status']['wan']['devices']

        result = None
        for aName in list(radios.keys()):
            
            if('ethernet' not in aName):
                result = radios[aName]

        return result

    def getJSON(self):

        try:
            r = requests.get(
                self.getAddress(),
                auth=self.getAuth(),
                verify=False
            )
        except:
            print 'UNKNOWN - Error when contacting Cradlepoint device: ' + str(sys.exc_info())
            sys.exit(3)

        if r.ok:
            try:
                return r.json()
            except:
                print 'UNKNOWN - Error when contacting Cradlepoint device: ' + str(sys.exc_info())
                sys.exit(3)


def main():

    parser = argparse.ArgumentParser(description="Checks Cradlepoint 600 Modem via Http API")
    parser.add_argument('-H','--host',required=True,type=str,help='Modem IP to check')
    parser.add_argument('-P','--port',required=True,type=int,help="Port of HTTP service")
    parser.add_argument('-p','--password',required=True,type=str,help="Password to authenticate")
    parser.add_argument('-t','--type',required=True,type=str,help="Type of check to perform (wifi|vpn|imei|phone|signal)")
    parser.add_argument('-T','--tunnel',required=False,type=str,help="Tunnel name if using VPN check")
    parser.add_argument('-c','--critical',required=False,type=int,help="critical value")
    parser.add_argument('-w','--warning',required=False,type=int,help="warning value")
    
    args = parser.parse_args(sys.argv[1:])

    host = HttpGetter(args.host,args.port,args.password)

    if(args.type == 'wifi'):
        check_wifi(host,args.critical)
    elif(args.type == 'vpn'):
        check_vpn(host,args.tunnel)
    elif(args.type == 'imei'):
        get_imei(host)
    elif(args.type == 'phone'):
        get_phone(host)
    elif(args.type == 'signal'):
        get_signal(host,args.warning,args.critical)
    else:
        print "Unknown type: " + args.type
        sys.exit(3)

def check_wifi(host,critical):
    json = host.getJSON()

    #check if the wifi radio is on
    status = json['data']['status']['wlan']['state']

    print "Wifi Radio is " + status

    #if on and we don't want it on
    if(status == 'On' and critical == 1):
        sys.exit(1)
    #if off and we don't want it off
    elif (status == 'Off' and critical == 0):
        sys.exit(1)
    else:
        sys.exit(0)

def check_vpn(host,tunnel):
    json = host.getJSON()

    #find the tunnel
    tunnelObj = None

    for aTunnel in json['data']['status']['vpn']['tunnels']:
        if(aTunnel['name'] == tunnel):
            tunnelObj = aTunnel

    if(tunnelObj != None):
        if(len(tunnelObj['connections']) < 1 or tunnelObj['connections'][0]['state'] != 'mature'):
            print tunnelObj['name'] + " is down"
            sys.exit(2)
        else:
            print tunnelObj['name'] + " is up"
            sys.exit(0)
    else:
        print tunnel + ' is not a valid name'
        sys.exit(3)

def get_imei(host):
    json = host.getJSON()

    radio = host.findVZWInfo(json)

    if(radio != None):
        print radio['diagnostics']['DISP_IMEI']
        sys.exit(0)
    else:
        print "Can't find radio information"
        sys.exit(3)

def get_phone(host):
    json = host.getJSON()

    radio = host.findVZWInfo(json)

    if(radio != None):
        print radio['diagnostics']['MDN']
        sys.exit(0)
    else:
        print "Can't find radio information"
        sys.exit(3)

def get_signal(host,warn,crit):
    json = host.getJSON()

    radio = host.findVZWInfo(json)

    if(radio != None):

        signal = int(radio['status']['signal_strength'])
        print  str(signal) + "%"
        
        if(signal <= crit):
            sys.exit(2)
        elif(signal <= warn):
            sys.exit(1)
        else:
            sys.exit(0)
    else:
        print "Can't find radio information"
        sys.exit(3)

if __name__ == '__main__':
    main()
