#!/bin/bash
# diff + vim result -- if no diff just print "No difference"

DIF=$(mktemp --suffix .diff)
diff -r $1 $2 > $DIF

if [ $? == 0 -o $? == 1 ]
then
	if [ -s $DIF ]
	then
		vim $DIF
	else
		echo "$0: No difference."
	fi
fi

rm $DIF
