"""Check the connection status of a VPN connection on a Fortigate Firewall. The hnmp library needs to be installed"""
import argparse
import sys
import datetime
from hnmp import SNMP,SNMPError

#uses hnmp library https://github.com/trehn/hnmp
#pip install hnmp

__author__ = "Rob Weber"
__email__ = "rweber@ecec.com"
__version__ = "1.1"

#parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument('-c','--community',required=True,help='The community string')
parser.add_argument('-H','--host',required=True,help='The host address')
parser.add_argument('-p','--peer',required=False,help='The peer name to look for')

args = parser.parse_args()

#setup the snmp object
snmp = SNMP(args.host, community=args.community)

#create table of peers https://community.fortinet.com/t5/FortiGate/Technical-Tip-OIDs-for-monitoring-IPsec-tunnel-status/ta-p/199930
peers = None
try:
    peers = snmp.table('1.3.6.1.4.1.12356.101.12.2.2.1', columns={2: "name", 4: "ip", 20: "status"}, 
            column_value_mapping={"status": {1: "Disconnected", 2: "Connected" }}, fetch_all_columns=False)
except SNMPError:
    print('Could not reach server at ' + args.host)
    sys.exit(1)

#print total if peer not given
if(args.peer == None):
    print('There are ' + str(len(peers.columns['name'])) + ' tunnels')
    sys.exit(0)
else:
    #if peer exists
    if(args.peer in peers.columns['name']):
        index = peers.columns['name'].index(args.peer)
        if(peers.rows[index]['status'] == 'Connected'):
            print(('%s (%s) is connected') % (args.peer, peers.rows[index]['ip']))
            sys.exit(0)
        else:
            print('%s (%s) is not connected' % (args.peer, peers.rows[index]['ip']))
            sys.exit(2)
    else:
        print(args.peer + ' is not in the list')
        sys.exit(2)
