#check temperature from Adruino temperature unit
ADDRESS=$1
WARNING_LIMIT=$2
CRIT_LIMIT=$3
RETURN=0

RESPONSE=$(curl $ADDRESS -s)

if [ -z $RESPONSE ]; then
  echo "Temperature sensor is down"
  exit 2
fi

TEMP=$(python -c "import json,sys;obj=json.loads('$RESPONSE');print obj['temperature']")
HUMID=$(python -c "import json,sys;obj=json.loads('$RESPONSE');print obj['humidity']")

#check if the sensor is returning bogus values
if [ $TEMP -eq 32 ]
then
  echo "Temperature sensor is reporting 0 (down)"
  exit 2
fi

if [ $TEMP -gt $CRIT_LIMIT ]
then
 RETURN=2
elif [ $TEMP -gt $WARNING_LIMIT ]
then
 RETURN=1
fi

echo "Temperature is $TEMP, Humidity is $HUMID%"

#echo $RETURN
exit $RETURN
