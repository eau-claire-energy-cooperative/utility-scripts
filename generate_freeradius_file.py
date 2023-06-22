#!/usr/bin/env python3
"""Generate a freeradius authorization file from a spreadsheet
For more information on protocol and password compatability see this chart:
http://deployingradius.com/documents/protocols/compatibility.html
"""
import argparse, binascii, hashlib, pandas, re, sys

__author__ = "Rob Weber"
__email__ = "rweber@ecec.com"
__version__ = "1.2"

RECORD_TYPES = ['generic', 'phone']
PASSWORD_TYPES = ['clear', 'md5', 'nt', 'none']
PASSWORD_MATRIX = {'clear': 'Cleartext-Password', 'md5': 'MD5-Password', 'nt': 'NT-Password'}

def is_mac(username):
  return re.search("^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", username.strip())

def generate_control_pairs(controls):
  if(len(controls) > 0):
    return ", " + ', '.join(controls)
  else:
    return ""

def generate_auth_line(username, password, r_type, p_type):
  control_pairs = []

  # set type to generic if it doesn't exist
  if(r_type not in RECORD_TYPES):
    print(f"Record type {r_type} doesn't exist, setting to generic")
    r_type = 'generic'

  if(p_type not in PASSWORD_TYPES):
    print(f"Auth Type {p_type} doesn't exist, setting to clear")
    p_type = 'clear'

  # any custom type settings
  if(r_type == 'phone'):
    # set the control pair
    calling_station = username.upper()
    calling_station = "-".join(calling_station[i:i+2] for i in range(0,12,2))
    control_pairs.append(f"Calling-Station-Id == \"{calling_station}\"")

  # if username is a MAC format for sent format
  if(is_mac(username)):
    username = username.replace('-', '').replace(':','').lower()

  # generate a password if one isn't set
  if(pandas.isnull(password)):
    # reverse the username to create a password
    password = username[::-1]

  if(p_type != 'clear'):
    # modify the password for the correct type
    if(p_type == 'nt'):
      hash = hashlib.new('md4', password.encode('utf-16le')).hexdigest()
      password = hash.upper()
    if(p_type == 'md5'):
      hash = hashlib.md5(password.encode())
      password = hash.hexdigest()

  if(p_type != 'none'):
    return f"{username}  {PASSWORD_MATRIX[p_type]} := {password}{generate_control_pairs(control_pairs)}"
  else:
    return f"{username}  {generate_control_pairs(control_pairs)}"

#setup the cli parser
parser = argparse.ArgumentParser(description='generate a freeradius authorization file from a spreadsheet')
parser.add_argument('-i', '--input_file', required=True, help='Path to a CSV file to read')
parser.add_argument('-o', '--output_file', required=False, type=str, default='authorize.txt',
                   help='Path to the output file, default authorize.txt')
parser.add_argument('-A', '--append', action='store_true',
                   help='Append the output file instead of overwriting it, default is no')
parser.add_argument('-u', '--user_column', required=False, type=int, default=1, help='Column number that contains the username')
parser.add_argument('-p', '--pass_column', required=False, type=int, default=2, help='Column number that contains the password')
parser.add_argument('-t', '--type_column', required=False, type=int, default=0,
                   help='Column number that contains the device type column, options are phone, or generic. -1 assumes all types are generic (no designated column)')
parser.add_argument('-a','--auth_column', required=False, type=int, default=-1,
                   help="Column number that contains the auth type column, options are none, clear, md5 or nt. -1 defaults to clear text (no designated column)")
parser.add_argument('-v','--vlan', required=False, type=int,
                   help="If a VLAN should be returned as part of the auth response - default is no")
args = parser.parse_args(sys.argv[1:])

print(f"Generating FreeRadius users file from: {args.input_file}")
print(f"Writing output to {args.output_file}")

# open the document
document = pandas.read_csv(args.input_file)
print(f"Loaded document has {len(document.index)} records")

# file mode is either write or append
file_mode = 'a' if args.append else 'w'

# write each line to the output file
with open(args.output_file, file_mode) as f:
  # iterate over each row
  for index, row in document.iterrows():
    record_type = 'generic' if args.type_column == -1 else row[args.type_column].lower()

    password_type = 'clear' if args.auth_column == -1 else row[args.auth_column].lower()

    f.write(generate_auth_line(row[args.user_column], row[args.pass_column], record_type, password_type))
    f.write("\n")

    accept_reply = []
    if(args.vlan):
        # if a vlan is given, add it as part of the reply
        accept_reply.append('Tunnel-Type = VLAN')
        accept_reply.append('Tunnel-Medium-Type = IEEE-802')
        accept_reply.append(f'Tunnel-Private-Group-Id = "{args.vlan}"')

    if(record_type == 'phone'):
        accept_reply.append('Cisco-AVPair = "device-traffic-class = voice"')

    if(len(accept_reply) > 0):
        f.write(f'\t{", ".join(accept_reply)}')
        f.write('\n')

