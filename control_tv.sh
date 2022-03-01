# send a command to the TV via the HDMI CEC
# ./control_tv standby - turn off TV
# ./control_tv.sh on - turn on the tV
COMMAND=$1

echo "$COMMAND 0.0.0.0" | cec-client -s -d 1
