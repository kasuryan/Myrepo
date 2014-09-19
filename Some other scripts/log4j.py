#!/usr/bin/python
'''
Script that is being remotely run on a set of hosts that need some modification for log rotation in the config files, followed by restart of the application to pick up the new configuration.
'''
import sys
import os
os.system("ls -lrth /usr/local/bbops/wals/logs/wals.log")
file = open("/usr/local/bbops/wals/conf/log4j.properties","a")
file.write("log4j.appender.LOGFILE.MaxBackupIndex=4\n")
file.write("log4j.appender.LOGFILE.MaxFileSize=200MB\n")
file.close()
os.system("sed -i s/FileAppender/RollingFileAppender/ /usr/local/bbops/wals/conf/log4j.properties")
os.system("/usr/local/bbops/wals/bin/wals.sh stop")
os.system("/usr/local/bbops/wals/bin/wals.sh start > /dev/null")
os.system("sleep 10;ls -lrth /usr/local/bbops/wals/logs/wals.log")
os.system("echo =================================================================================================")
sys.exit()
