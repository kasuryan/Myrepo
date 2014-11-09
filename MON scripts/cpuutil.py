#!/usr/bin/env python
#
# cpuutil.py 
# This is a Wily EPAgent script that monitors CPU Utilization
#

# - user: normal processes executing in user mode
# - nice: niced processes executing in user mode
# - system: processes executing in kernel mode
# - idle: twiddling thumbs
# - iowait: waiting for I/O to complete
# - irq: servicing interrupts
# - softirq: servicing softirqs
# - steal: involuntary wait
# - guest: running a normal guest
# - guest_nice: running a niced guest

import time
import sys

def printcpu(cpu, curr, old):
	old_total=0.0
	curr_total=0.0
	for word in old:
		if word.startswith('cpu') == False:
			old_total += int(word)
	for word in curr:
		if word.startswith('cpu') == False:
			curr_total += int(word)
	total   = curr_total-old_total
	user    = float(curr[1])-float(old[1])
	nice    = float(curr[2])-float(old[2])
	system  = float(curr[3])-float(old[3])
	idle    = float(curr[4])-float(old[4])
	iowait  = float(curr[5])-float(old[5])
	irq     = float(curr[6])-float(old[6])
	softirq = float(curr[7])-float(old[7])
	steal   = 0.0
	if len(curr) >= 10 and len(old) >= 10:
		steal = float(curr[8])-float(old[8])
	
	print ('<metric type="IntAverage" name="Resource Usage|CPU Utilization|%s:User (%%)" value="%d" />' % (cpu, user*100/total));
	print ('<metric type="IntAverage" name="Resource Usage|CPU Utilization|%s:Nice (%%)" value="%d" />' % (cpu, nice*100/total));
	print ('<metric type="IntAverage" name="Resource Usage|CPU Utilization|%s:System (%%)" value="%d" />' % (cpu, system*100/total));
	print ('<metric type="IntAverage" name="Resource Usage|CPU Utilization|%s:Idle (%%)" value="%d" />' % (cpu, idle*100/total));
	print ('<metric type="IntAverage" name="Resource Usage|CPU Utilization|%s:I/O Wait (%%)" value="%d" />' % (cpu, iowait*100/total));
	print ('<metric type="IntAverage" name="Resource Usage|CPU Utilization|%s:IRQ (%%)" value="%d" />' % (cpu, irq*100/total));
	print ('<metric type="IntAverage" name="Resource Usage|CPU Utilization|%s:Soft IRQ (%%)" value="%d" />' % (cpu, softirq*100/total));
	print ('<metric type="IntAverage" name="Resource Usage|CPU Utilization|%s:Steal (%%)" value="%d" />' % (cpu, steal*100/total));


f = open('/proc/stat', 'r')
values = dict()
oldvalues = values
while True:
	f.seek(0)
	while True:
		line = str.split(f.readline())
		if len(line) == 0:
			break;
		if line[0].startswith('cpu'):
			values[line[0]] = line
			if values is not oldvalues and line[0] == 'cpu':
				printcpu("Total", values[line[0]], oldvalues[line[0]])
			elif values is not oldvalues:
				printcpu(line[0], values[line[0]], oldvalues[line[0]])

	oldvalues = dict(values)
	sys.stdout.flush();
	time.sleep(1)
