#./bin/bash
if [ -z $1 ]
then
	echo "please input direction tx or rx"
else
	if [ -z $2 ]
	then
			echo "Please duation to sleep"
	else
		if [ -z $3 ]
		then
			echo "Please # of iteration"
		else
			echo "$1 direction"
			echo "$2 duration of sleep"
			echo "$3 iteration"
			for ((i=1; i<=$3 ; i++))
				do
					echo "$i/$3 th run"
					echo "python iperf_auto.py -ipd 192.168.1.4 -ipp 192.168.1.3 -b a -t tcp -x $1 -lc PHONE -d 60 -s $2 "
					python iperf_auto.py -ipd 192.168.1.9 -ipp 192.168.1.3 -b a -t tcp -x $1 -lc PHONE -d 60 -s $2
					sleep 5
				done
		fi
	fi
fi
