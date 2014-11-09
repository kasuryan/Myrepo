#!/usr/bin/env python
#
# This is a Wily EPAgent script that monitors disk statistics
#
##### Fields in /proc/diskstats
#
# Field  0 - Major number of device
# Field  1 - Minor number of device
# Field  2 - Device short name
# Field  3 - Number of reads completed
# Field  4 - Number of reads merged
# Field  5 - Number of sectors read
# Field  6 - Number of milliseconds spent reading
# Field  7 - Number of writes completed
# Field  8 - Number of writes merged
# Field  9 - Number of sectors written
# Field 10 - Number of milliseconds spent writing
# Field 11 - Number of I/Os currently in progress
# Field 12 - Number of milliseconds spent doing I/Os
# field 13 - Weighted number of milliseconds spent doing I/Os
#
#####

import time
import sys


def printdiskstats(disk, values, oldvalues, curr_time, old_time):
	elapsed = curr_time-old_time
	rd_merges = int(values[4])-int(oldvalues[4])
	wr_merges = int(values[8])-int(values[8])
	rd_ios = int(values[3])-int(oldvalues[3])
	wr_ios = int(values[7])-int(oldvalues[7])
	nr_ios = rd_ios+wr_ios
	rd_sectors = int(values[5])-int(oldvalues[5])
	wr_sectors = int(values[9])-int(oldvalues[9])
	rd_ticks = int(values[6])-int(oldvalues[6])
	wr_ticks = int(values[10])-int(oldvalues[10])
	tot_ticks = int(values[12])-int(oldvalues[12])
	rq_ticks = int(values[13])-int(oldvalues[13])

	util = round((100*tot_ticks)/(elapsed*1000)) # Percentage * 100
	avgq_sz = round(rq_ticks/(elapsed*1000))
	if nr_ios != 0:
		await = round((rd_ticks + wr_ticks)/nr_ios)
	else:
		await = 0
	if nr_ios != 0:
		arqsz = round((rd_sectors + wr_sectors)/nr_ios)
	else:
		arqsz = 0

	print ('<metric type="longAverage" name="Resource Usage|Disk Statistics|%s:Reads per second" value="%d" />' % (disk, round(rd_ios/elapsed)))
	print ('<metric type="longAverage" name="Resource Usage|Disk Statistics|%s:Reads merged per second" value="%d" />' % (disk, round(rd_merges/elapsed)))
	print ('<metric type="longAverage" name="Resource Usage|Disk Statistics|%s:Sectors read per second" value="%d" />' % (disk, round(rd_sectors/elapsed)))
	print ('<metric type="longAverage" name="Resource Usage|Disk Statistics|%s:Writes per second" value="%d" />' % (disk, round(wr_ios/elapsed)))
	print ('<metric type="longAverage" name="Resource Usage|Disk Statistics|%s:Writes merged per second" value="%d" />' % (disk, round(wr_merges/elapsed)))
	print ('<metric type="longAverage" name="Resource Usage|Disk Statistics|%s:Sectors written per second" value="%d" />' % (disk, round(wr_sectors/elapsed)))
	print ('<metric type="longAverage" name="Resource Usage|Disk Statistics|%s:I/O per second" value="%d" />' % (disk, round(rd_ios+wr_ios)/elapsed))
	print ('<metric type="intAverage" name="Resource Usage|Disk Statistics|%s:Utilization (%%)" value="%d" />' % (disk, util))
	print ('<metric type="longAverage" name="Resource Usage|Disk Statistics|%s:Average wait time (ms)" value="%d" />' % (disk, await))
	print ('<metric type="longAverage" name="Resource Usage|Disk Statistics|%s:Average queue size" value="%d" />' % (disk, avgq_sz))
	print ('<metric type="longAverage" name="Resource Usage|Disk Statistics|%s:Average request size" value="%d" />' % (disk, arqsz))
	
	

f = open('/proc/diskstats', 'r')
values = dict()
oldvalues = values
while True:
	f.seek(0)
	while True:
		total = 0.0
		curr_time = time.time()
		line = str.split(f.readline())
		if len(line) == 0:
			break;
		values[line[2]] = line
		line2 = line[2]
		if (line2[:2] == 'vd' or line2[:2] == 'sd' or line2[:2] == 'hd') and not line2[-1:].isdigit():
			if values is not oldvalues:
				printdiskstats(line2, values[line2], oldvalues[line2], curr_time, old_time)

	oldvalues = dict(values)
	old_time = curr_time
	sys.stdout.flush();
	time.sleep(1)
