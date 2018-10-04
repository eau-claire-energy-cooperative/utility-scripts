#!/usr/bin/env python
"""check various endpoints on HP MSA devices (1040,2050,2052) """
import argparse
import types
import sys
import xml.dom.minidom
import requests
import hashlib
from requests.auth import HTTPDigestAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning,InsecurePlatformWarning,SNIMissingWarning

#disable insecure request warnings
requests.packages.urllib3.disable_warnings((InsecureRequestWarning,InsecurePlatformWarning,SNIMissingWarning))

class HttpGetter:
    address = None
    secret = None
    session = None
    
    def __init__(self,host,username,password,secure):
        
        #build the URL
        if(secure):
            self.address = 'https://%s/api/' % (host)
        else:
            self.address = 'http://%s/api' % (host)

        #create the authentication hash
        md5 = hashlib.md5()
        md5.update(str(username + "_" + password).encode('utf-8'))
        self.secret = '/api/login/%s' % (md5.hexdigest())
        
    def _auth(self):
        
        #authenticate
        try:
            r = requests.post(
                self.address,
                verify=False,
                data=self.secret
            )
        except:
            print('UNKNOWN - Error when contacting MSA: ' + str(sys.exc_info()))
            sys.exit(3)

        if(r.ok):
            success = False
            try:
                #get the text
                doc = xml.dom.minidom.parseString(r.text)
                
                for property in doc.getElementsByTagName('PROPERTY'):
                    #if this is the response type
                    if(property.getAttribute('name') == 'response-type'):
                        if(property.firstChild.nodeValue == 'success'):
                            success = True
                        elif(property.firstChild.nodeValue == 'error'):
                            print('UNKNOWN - Authentication Error')
                            sys.exit(3)
                if(success):
                    #get the session key
                    prop = doc.getElementsByTagName("PROPERTY")[2]
                    self.session = prop.firstChild.nodeValue
                    
            except:
                print('UNKNOWN - Error when contacting MSA: ' + str(sys.exc_info()))
                sys.exit(3)

    def _httpGet(self,command):
        #run command on MSA
        r = requests.get(
            command,
            verify=False,
            cookies = {"wbisessionkey":self.session,'wbiusername':''},
            data=''
        )

        #parse xml
        return xml.dom.minidom.parseString(r.text)
                
    def _findPropStatus(self,xml,propertyName):
        result = None
        for prop in xml:
            if(prop.getAttribute(propertyName['name']) == propertyName['value']):
                result = prop.firstChild.nodeValue
        
        if(result == None):
            print('UNKNOWN - Error parsing MSA response')
            sys.exit(3)
        
        return result

    def _runCommand(self,command,objName,propName,propValue):
        result = []
        
        try:
            doc = self._httpGet("%s%s" % (self.address,command))
            
            for obj in doc.getElementsByTagName('OBJECT'):
                
                if(obj.getAttribute('name') == objName):
                    result.append(self._findPropStatus(obj.getElementsByTagName('PROPERTY'),{'name':propName,'value':propValue}))
            
        except:
            print('UNKNOWN - Error parsing xml: ' + str(sys.exc_info()))
            sys.exit(3)
            
        return result
    
    def _findSensorTypes(self,command):
        result = {}
        allowed = ['Temperature','Voltage','Overall']
        try:
            doc = self._httpGet("%s%s" % (self.address,command))
            
            for obj in doc.getElementsByTagName("OBJECT"):
                
                if(obj.getAttribute('name') == 'sensor'):
                    #get the sensor type
                    typeName = self._findPropStatus(obj.getElementsByTagName("PROPERTY"),{'name':'name','value':'sensor-type'})
                    
                    if(typeName in allowed):
                        if(typeName not in result):
                            result[typeName] = []
                    
                        result[typeName].append(self._findPropStatus(obj.getElementsByTagName("PROPERTY"),{'name':'name','value':'status'}))
            
        except:
            print('UNKNOWN - Error parsing xml: ' + str(sys.exc_info()))
            sys.exit(3)
                
        return result
    
    def _findFRU(self,command):
        result = {}
        try:
            doc = self._httpGet("%s%s" % (self.address,command))
            
            for obj in doc.getElementsByTagName("OBJECT"):
                
                if(obj.getAttribute('name') == 'fru'):
                    #get the sensor type
                    typeName = self._findPropStatus(obj.getElementsByTagName("PROPERTY"),{'name':'name','value':'fru-shortname'})
                    
                    if(typeName not in result):
                        result[typeName] = []
                    
                    result[typeName].append(self._findPropStatus(obj.getElementsByTagName("PROPERTY"),{'name':'name','value':'fru-status'}))
            
        except:
            print('UNKNOWN - Error parsing xml: ' + str(sys.exc_info()))
            sys.exit(3)
                
        return result
    
    def getStatus(self):
        statuses = {}
        
        #authenticate
        if(self.session == None):
            self._auth()

        #get the disk status
        statuses['Disk'] = self._runCommand("show/disks",'drive','name','health')
        statuses['Vdisk'] = self._runCommand("show/vdisks",'virtual-disk','name','health')
        statuses['Enclosure'] = self._runCommand("show/enclosures",'enclosures','name','health')
        
        #get special cases
        statuses.update(self._findSensorTypes("show/sensor-status"))
        statuses.update(self._findFRU('show/frus'))
        
        #go through each and record state
        output = ''
        overallStatus = 'OK'
        
        for aType in statuses.keys():
            #record values for each type
            output = output + aType
            crit = 0
            warn = 0
            ok = 0
            
            for aStatus in statuses[aType]:
                if(aStatus == 'OK'):
                    ok = ok + 1
                elif(aStatus == 'Warning'):
                    warn = warn + 1
                elif(aStatus == 'Fault'):
                    crit = crit + 1
                else:
                    crit = crit + 1
                
            if(warn > 0 and crit == 0):
                output = "%s %d Warning, " % (output,warn)
                overallStatus = "Warning"
            
            if(crit > 0):
                output = "%s %d Critical, " % (output,crit)
                overallStatus = "Critical"
                
            if(warn == 0 and crit == 0):
                output = "%s %d OK, " % (output,ok)
            
        print(output)
        
        #exit with correct error
        if(overallStatus == 'OK'):
            sys.exit(0)
        elif(overallStatus == 'Warning'):
            sys.exit(1)
        elif(overallStatus == 'Critical'):
            sys.exit(2)
            
def main():

    parser = argparse.ArgumentParser(description="Checks status of HP MSA devices via web API")
    parser.add_argument('-H','--host',required=True,type=str,help='IP of the MSA')
    parser.add_argument('-U','--username',required=True,type=str,help="MSA username")
    parser.add_argument('-P','--password',required=True,type=str,help="Password to authenticate")
    parser.add_argument('-s','--secure',required=False,type=bool,help="secure connection",default=False)
    
    args = parser.parse_args(sys.argv[1:])

    host = HttpGetter(args.host,args.username,args.password,args.secure)
    host.getStatus()

if __name__ == '__main__':
    main()
