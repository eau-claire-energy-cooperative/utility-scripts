#check status of icinga2 config file
if /usr/sbin/icinga2 daemon -C > /dev/null 2>&1; then
	echo "Icinga config file is correct"
	return 0
else
	echo "Icinga config file is incorrect"
	/usr/sbin/icinga2 daemon -C | grep "Error"
	return 2
fi

