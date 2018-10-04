"""Check the status of a switch port on a Cisco switch, goal is to make sure non-allowed interfaces are not being used"""
import argparse
import sys
import datetime
from hnmp import SNMP,SNMPError

IF_UP = 1
IF_DOWN = 2

#uses hnmp library https://github.com/trehn/hnmp
#pip install hnmp

#parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument('-c','--community',required=True,help='The community string')
parser.add_argument('-H','--host',required=True,help='The host address')
parser.add_argument('-u','--up',required=False,help='list of interfaces that should be up')

args = parser.parse_args()

#setup the snmp object
snmp = SNMP(args.host, community=args.community)

#create table of interfaces http://www.alvestrand.no/objectid/1.3.6.1.2.1.2.2.1.3.html
interfaces = None
try:
    interfaces = snmp.table('1.3.6.1.2.1.2.2.1',columns={1:"index",2:"description",8:"status",3:"type"},fetch_all_columns=False)
except SNMPError:
    print('Could not reach server at ' + args.host)
    sys.exit(1)

#print
if(interfaces != None):
    interfacesUp = []
    for index in range(0,len(interfaces.columns['description'])):
        if(interfaces.columns['status'][index] == IF_UP and interfaces.columns['type'][index] == 6):
            interfacesUp.append(interfaces.columns['description'][index])

    #interfaces that are up but shouldn't be
    badInterfaces = [i for i in interfacesUp if i not in args.up]

    if(len(badInterfaces) > 0):
        print("The following interfaces are active: %s" % (', '.join(badInterfaces)))
        sys.exit(2)

print("No unauthorized interfaces active")
sys.exit(0)

