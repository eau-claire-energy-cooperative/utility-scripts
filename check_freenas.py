#!/usr/bin/env python
"""Check various services on a FreeNAS server using the built in API. Use -h for more info"""
import argparse
import json
import sys
import requests
import math

class Startup(object):
 
    def __init__(self, hostname, user, secret):
        self._hostname = hostname
        self._user = user
        self._secret = secret
 
        self._ep = 'http://%s/api/v1.0' % hostname
 
    def request(self, resource, method='GET', data=None):
        if data is None:
            data = ''
        try:
            r = requests.request(
                method,
                '%s/%s/' % (self._ep, resource),
                data=json.dumps(data),
                headers={'Content-Type': "application/json"},
                auth=(self._user, self._secret),
            )
        except:
            print 'UNKNOWN - Error when contacting freenas server: ' + str(sys.exc_info())
            sys.exit(3)
 
        if r.ok:
            try:
                return r.json()
            except:
                print 'UNKNOWN - Error when contacting freenas server: ' + str(sys.exc_info())
                sys.exit(3)
 
    def check_repl(self):
        repls = self.request('storage/replication')
        errors=0
        try:
            for repl in repls:
                if repl['repl_status'] != 'Succeeded':
                    errors = errors + 1
        except:
            print 'UNKNOWN - Error when contacting freenas server: ' + str(sys.exc_info())
            sys.exit(3)
 
        if errors > 0:
            print 'WARNING - There are ' + str(errors) + ' replication errors. Go to Storage > Replication Tasks > View Replication Tasks in FreeNAS for more details.'
            sys.exit(1)
        else:
            print 'OK - No replication errors'
            sys.exit(0)
 
    def check_alerts(self):
        alerts = self.request('system/alert')
        errors=0
        try:
            for alert in alerts:
                if alert['level'] != 'OK':
                    errors = errors + 1
        except:
            print 'UNKNOWN - Error when contacting freenas server: ' + str(sys.exc_info())
            sys.exit(3)
 
        if errors > 0:
            print 'WARNING - There are ' + str(errors) + ' alerts. Click Alert button in FreeNAS for more details.'
            sys.exit(1)
        else:
            print 'OK - No problem alerts'
            sys.exit(0)

    def check_volume_size(self,warn,crit):
        volumes = self.request('storage/volume/')
        exit_code = 0
        
        try:
            for volume in volumes:
                print 'Volume ' + volume['name'] + ' has ' + volume['used_pct'] + ' used of ' + str(self.convertBytes(volume['avail'],'GB')) + 'GB'
                percentUsed = int(volume['used_pct'][:-1])

                if(percentUsed >= warn and exit_code <= 1):
                    exit_code = 1
                elif(percentUsed >= crit and exit_code <= 2):
                    exit_code = 2
                    
        except:
            print 'UNKNOWN - Error when contacting the freenas server: ' + str(sys.exc_info())
            sys.exit(3)

        sys.exit(exit_code)

    def check_volume_status(self):
        volumes = self.request('storage/volume/')
        exit_code = 0

        try:
            for volume in volumes:
                print 'Volume ' + volume['name'] + ' is ' + volume['status']

                if(volume['status'] != 'HEALTHY'):
                    exit_code = 2
                
        except:
            print 'UNKNOWN - Error when contacting the freenas server: ' + str(sys.exc_info())
            sys.exit(3)

        sys.exit(exit_code)

    def convertBytes(self,byteSize,convertTo):
        result = byteSize

        if(convertTo == 'KB'):
            result = byteSize/math.pow(2,10)
        elif(convertTo == 'MB'):
            result = byteSize/math.pow(2,20)
        elif(convertTo == 'GB'):
            result = byteSize/math.pow(2,30)
        elif(convertTo == 'TB'):
            result = byteSize/math.pow(2,40)

        return '{0:.3f}'.format(result)
 
def main():
    parser = argparse.ArgumentParser(description='Checks a freenas server using the API')
    parser.add_argument('-H', '--hostname', required=True, type=str, help='Hostname or IP address')
    parser.add_argument('-u', '--user', required=True, type=str, help='Normally only root works')
    parser.add_argument('-p', '--passwd', required=True, type=str, help='Password')
    parser.add_argument('-t', '--type', required=True, type=str, help='Type of check (alerts,repl,vol_size,vol_status)')
    parser.add_argument('-c', '--crit',required=False,type=int,help='Critical percent to check (volume check only')
    parser.add_argument('-w', '--warn',required=False,type=int,help='Warning percent to check (volume check only')

    args = parser.parse_args(sys.argv[1:])
 
    startup = Startup(args.hostname, args.user, args.passwd)
 
    if args.type == 'alerts':
        startup.check_alerts()
    elif args.type == 'repl':
        startup.check_repl()
    elif args.type == 'vol_size':
        startup.check_volume_size(args.warn,args.crit)
    elif args.type == 'vol_status':
        startup.check_volume_status()
    else:
        print "Unknown type: " + args.type
        sys.exit(3)
 
if __name__ == '__main__':
    main()
