"""Check the SSIDs and client counts of a Unifi wifi device. The hnmp library needs to be installed"""
import argparse
import sys
import functools
from hnmp import SNMP, SNMPError

#uses hnmp library https://github.com/trehn/hnmp
#pip install hnmp

__author__ = "Rob Weber"
__email__ = "rweber@ecec.com"
__version__ = "1.1"

#parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--community', required=True, help='The community string')
parser.add_argument('-H', '--host', required=True, help='The host address')
parser.add_argument('-d', '--device', required=False, help='check the total device count', action='store_true')
parser.add_argument('-w', '--warning', required=False, help='the client count to show a warning', type=int)
args = parser.parse_args()

snmp = SNMP(args.host, community=args.community)

#create snmp table based on UBNT OIDs
table = None
try:
  table = snmp.table('.1.3.6.1.4.1.41112.1.6.1.2.1', columns={6: 'ssid', 8: 'clients', 9: 'radio'})
except SNMPError as e:
  print('error')
  print(e)
  sys.exit(1)

if(table is not None):

  #get the available SSIDs
  allNames = {}
  index = 0
  for ssid in table.columns['ssid']:
    if(ssid not in allNames and ssid != ''):
      allNames[ssid] = int(table.columns['clients'][index])
    index = index + 1

  if(not args.device):
    #just print the ssid information
    print('SSIDs: %s' % ', '.join(allNames.keys()))
  else:
    #check the client total
    clients = functools.reduce(lambda a,b : a+b, allNames.values())
    print('Total Clients: %d' % clients);

    if(args.warning is not None and clients >= args.warning):
      print('warn')
      sys.exit(1)
    else:
      sys.exit(0)
