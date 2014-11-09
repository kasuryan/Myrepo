#!/usr/bin/env python
#
# procmon.py
#
# This is a Wily EPAgent script that monitors process based on procmon.cfg
#

import time;
import os;
import re;
import sys;
import ConfigParser;

def printMetric(mType,mName,mValue):
        print "<metric type=\"%s\" name=\"Process|%s:Number of Running Processes\" value=\"%s\" />" % (mType,mName,mValue)

def loadCfg():
        global procList;
        config = ConfigParser.ConfigParser()
        config.readfp(open(os.path.dirname(os.path.realpath(__file__))+'/procmon.cfg'))
        procList = config.items('proc');
        if len(procList) == 0:
                print("proc list to monitor is empty and/or can not load procmon.cfg")
                sys.exit(0)

loadCfg()
procs = []
for proc in procList:
        matchs = re.compile(proc[1])
        procs.append([proc[0],matchs])

while 1:
    scriptErrors = 0
    try:
        dirs = [f for f in os.listdir('/proc/') if re.match(r'^[0-9]+$', f)]
        src = []
        for dir in dirs:
            try:
                f = open('/proc/'+dir+'/cmdline','r')
                src.append(f.read())
            except (IOError, OSError):
                scriptErrors += 1
                pass
            else:
                f.close()

        for proc in procs:
            count = 0
            for line in src:
                m = re.search(proc[1], line)
                if m:
                    count += 1
            printMetric('intCounter',proc[0],count)

    except (IOError, OSError):
        scriptErrors += 1
        pass
    print "<metric type=\"intCounter\" name=\"Process:safeScriptExceptions\" value=\"%s\" />" % (scriptErrors)
    sys.stdout.flush()
    time.sleep(5)
