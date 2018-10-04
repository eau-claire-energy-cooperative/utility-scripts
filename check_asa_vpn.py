"""Check the connection status of a VPN connection on a Cisco ASA. The hnmp library needs to be installed"""
import argparse
import sys
import datetime
from hnmp import SNMP,SNMPError

#uses hnmp library https://github.com/trehn/hnmp
#pip install hnmp

__author__ = "Rob Weber"
__email__ = "rweber@ecec.com"
__version__ = "1.0"

#parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument('-c','--community',required=True,help='The community string')
parser.add_argument('-H','--host',required=True,help='The host address')
parser.add_argument('-p','--peer',required=False,help='The peer address to look for')

args = parser.parse_args()

#setup the snmp object
snmp = SNMP(args.host, community=args.community)

#create table of peers http://www.oidview.com/mibs/9/CISCO-IPSEC-FLOW-MONITOR-MIB.html
peers = None
try:
    peers = snmp.table('1.3.6.1.4.1.9.9.171.1.2.3.1',columns={7:'ip',16:'active_time',20:'in_packets',28:'out_packets'})
except SNMPError:
    print('Could not reach server at ' + args.host)
    sys.exit(1)

#print total if peer not given
if(args.peer == None):
    print('There are ' + str(len(peers.columns['ip'])) + ' tunnel peers connected')
    sys.exit(0)
else:
    #if peer exists
    if(args.peer in peers.columns['ip']):
        index = peers.columns['ip'].index(args.peer)
        connected = datetime.timedelta(seconds=peers.rows[index]['active_time']/100) #hundreths of seconds
        
        print(('%s connected for %s') % (args.peer,connected))
        sys.exit(0)
    else:
        print(args.peer + ' is not connected')
        sys.exit(2)
