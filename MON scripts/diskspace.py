#!/usr/bin/env python
#
#
# This is a Wily EPAgent script that monitors disk space utilization
#

import os
import time
import sys

def print_metric(type, name, path, value):
	print('<metric type="%s" name="Resource Usage|Disk Space|%s:%s" value="%d" />' % (type, path, name, value))

    
while True:
    for line in open('/proc/mounts').readlines():
        fields = line.split()
        try:
            if not fields[0].startswith('/dev'):
                continue
            elif 'ro' in fields[3].split(','):
                # This is a readonly mount, so ignore it.
                continue
            stat = os.statvfs(fields[1])
        except (IndexError, OSError):
            # Malformed /proc/mounts (shouldn't ever happen) or unreadable
            # mount point.
            continue

        print_metric('LongAverage', 'Blocks Used', fields[1], stat.f_blocks - stat.f_bfree)
        print_metric('LongAverage', 'Blocks Free', fields[1], stat.f_bfree)
        print_metric('LongAverage', 'Blocks Total', fields[1], stat.f_blocks)
        print_metric('LongAverage', 'Bytes Total', fields[1], stat.f_blocks * stat.f_frsize)
        print_metric('LongAverage', 'Bytes Free', fields[1], stat.f_bfree * stat.f_frsize)
        print_metric('LongAverage', 'Bytes Used', fields[1], (stat.f_blocks - stat.f_bfree) * stat.f_frsize)
        print_metric('IntAverage', 'Utilization (%)', fields[1], 100.0 * (stat.f_blocks - stat.f_bavail) / stat.f_blocks)
        print_metric('IntAverage', 'Root Utilization (%)', fields[1], 100.0 * (stat.f_blocks - stat.f_bfree) / stat.f_blocks)

    sys.stdout.flush()
    time.sleep(5)

