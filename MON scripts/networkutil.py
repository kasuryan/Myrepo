#!/usr/bin/env python
#
# networkutil.py 
#
# This is a Wily EPAgent script that monitors network utilization for all interfaces.
#

import time
import sys

def printntw(interface, newvalues, oldvalues):
	print ('<metric type="longAverage" name="Resource Usage|Network Utilization|%s:Received bytes per second" value="%d" />' % (interface, float(newvalues[1])-float(oldvalues[1])))
	print ('<metric type="longAverage" name="Resource Usage|Network Utilization|%s:Received packets per second" value="%d" />' % (interface, float(newvalues[2])-float(oldvalues[2])))
	print ('<metric type="longAverage" name="Resource Usage|Network Utilization|%s:Received errors per second" value="%d" />' % (interface, float(newvalues[3])-float(oldvalues[3])))
	print ('<metric type="longAverage" name="Resource Usage|Network Utilization|%s:Received drops per second" value="%d" />' % (interface, float(newvalues[4])-float(oldvalues[4])))
	print ('<metric type="longAverage" name="Resource Usage|Network Utilization|%s:Sent bytes per second" value="%d" />' % (interface, float(newvalues[9])-float(oldvalues[9])))
	print ('<metric type="longAverage" name="Resource Usage|Network Utilization|%s:Sent packets per second" value="%d" />' % (interface, float(newvalues[10])-float(oldvalues[10])))
	print ('<metric type="longAverage" name="Resource Usage|Network Utilization|%s:Sent errors per second" value="%d" />' % (interface, float(newvalues[11])-float(oldvalues[11])))
	print ('<metric type="longAverage" name="Resource Usage|Network Utilization|%s:Sent drops per second" value="%d" />' % (interface, float(newvalues[12])-float(oldvalues[12])))

f = open('/proc/net/dev', 'r')
values = dict()
oldvalues = values
while True:
	f.seek(0)
	while True:
		# Sometimes the first two fields are only separated by a :, with no space
		# So we first replace the : with a space instead so that split works.
		line = f.readline().replace(':',' ', 1);
		line = line.split()
		if len(line) == 0:
			break;
		# Only print if the second column is a number; i.e. don't worry about headers
		if line[1].isdigit():
			values[line[0]] = line
			if (values is not oldvalues):
				printntw(line[0], values[line[0]], oldvalues[line[0]])

	oldvalues=dict(values)
	sys.stdout.flush();
	time.sleep(1)
