"""Check various endpoints of a Meraki cloud enabled device, requires nagious /check_snmp command to be available"""
import argparse
import sys
from subprocess import Popen,PIPE
import re


#A python class for querying the Meraki Cloud Controller.
#Setup SNMP under Organization->Settings in the Meraki cloud website
#run python meraki_ap.py --help to get a list of arguments
class MerakiSNMP:
    args = None
    oid_dict =  {"devStatus":{'oid':'.1.3.6.1.4.1.29671.1.1.4.1.3','title':'Device Status'},
                 "devProductCode":{"oid":".1.3.6.1.4.1.29671.1.1.4.1.9","title":"Device Type"},
                 "devContactedAt":{"oid":".1.3.6.1.4.1.29671.1.1.4.1.4","title":"Last Contacted"},
                 "devClientCount":{"oid":".1.3.6.1.4.1.29671.1.1.4.1.5","title":"Client Count"}}
    
    def __init__(self):
        mac = None

        #setup the parser
        parser = argparse.ArgumentParser()
        parser.add_argument('-m','--mac',help='MAC Address of the AP',required=True)
        parser.add_argument('-C','--command',required=True,choices=['devStatus','devProductCode','devContactedAt','devClientCount'],help='The command to run, valid values are devStatus,devProductCode,devClientCount,devContactedAt')
        parser.add_argument('-H','--host',required=True,help="The Meraki Controller address")
        parser.add_argument('-p','--port',required=True,help="The port for SNMP requests")
        parser.add_argument('-c','--community',required=True,help="The community string")
        
        self.args = parser.parse_args()


    def run(self):
	result = 0

        #first create the oid to query
        oid = self._createOID();

	#create the command string
	commandArray = ['/usr/lib/nagios/plugins/check_snmp','-H',self.args.host,'-p',self.args.port,'-C',self.args.community,'-P','2c','-o',oid]

	#send the command 
	process = Popen(commandArray,stdout=PIPE)
	(output,err) = process.communicate()

	pResult = process.wait()

        if(pResult == 0):
            #pull thetext we care about
            temp = output
            try:
                output = re.search('-\s(.+?)\s\|',output).group(1)
            except AttributeError:
                output = temp

            #process the result
            result = self._processResult(output.strip())
        else:
            print "Error contacting " + self.args.host
            result = pResult
            
	return result

    def _processResult(self,output):
        exit_code = 0
        
        if(self.args.command == 'devStatus'):
            if(int(output) != 1):
                exit_code = 2
                print self.oid_dict[self.args.command]['title'] + ": device is offline"
            else:
                print self.oid_dict[self.args.command]['title'] + ": device is online"
        elif(self.args.command == 'devProductCode'):
            print self.oid_dict[self.args.command]['title'] + ": " + output
        elif (self.args.command == 'devClientCount'):
            if(int(output) > 25):
                #throw a warning here, this is kind of alot
                exit_code = 1
            print self.oid_dict[self.args.command]['title'] + ": " + output
        elif (self.args.command == 'devContactedAt'):
            splitArray = output.split(' ')
            print str(int(splitArray[2],16)) + "-" + str(int(splitArray[3],16)) + "-" + str(int(splitArray[0] + splitArray[1],16)) + " " + str(int(splitArray[4],16) - int(splitArray[9],16)) + ":" + str(int(splitArray[5],16))
             
        return exit_code
                

    def _createOID(self):
        result = ''

        #convert mac to decimal notation
        macArray = self.args.mac.split(':')

        for aHex in macArray:
            result = result + "." + str(int(aHex,16))

        #add to oid
        result = self.oid_dict[self.args.command]['oid'] + result

        return result

#create the object
meraki = MerakiSNMP()
                
result = meraki.run()
sys.exit(result)
