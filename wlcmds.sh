#!/bin/bash
if [ -z $1 ]
then
        echo "please input time sleep"
else
echo " $1 seconds sleep during wl iterations"
adb shell wl reset_cnts;

while true;
	do
		date
		adb shell wl snr;
		adb shell wl rssi;
		adb shell wl counters;
		sleep $1 ;
	done
fi
