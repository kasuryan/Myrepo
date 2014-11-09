#!/usr/bin/env python
#
# loadavg.py 
#
# This is a Wily EPAgent script that monitors load average.
#

import time;
import sys;

f = open('/proc/loadavg', 'r')
while True:
	f.seek(0)
	args = str.split(f.read())
	print ('<metric type="longAverage" name="Resource Usage|Load Average x 100:01 Minute" value="%d" />' % (float(args[0])*100));
	print ('<metric type="longAverage" name="Resource Usage|Load Average x 100:05 Minutes" value="%d" />' % (float(args[1])*100));
	print ('<metric type="longAverage" name="Resource Usage|Load Average x 100:15 Minutes" value="%d" />' % (float(args[2])*100));
	sys.stdout.flush();
	time.sleep(1)

