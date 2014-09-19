#!/usr/local/bin/python2.7
'''
A small script that changes the DB string on a tomcat web application configuration file. First a backup of the file is made & then the DB connect string is replaced.
This script was written to minimize the time consuming task of changing it on some 35 odd hosts.
'''
import subprocess
import shlex
import sys

f=open("webconfighosts")
j=f.read().splitlines()
for i in j:
 i=i.strip()
 print i
 subprocess.call(['ssh','-i','/home/ksuryanarayanan/bbops_id_dsa',i,'mkdir /root/kartiktest;find /root/CRQ000020387930 -name webconfigure.properties.pre -exec cp {} /root/kartiktest/webconfigure.properties.pre.test \;'])
 subprocess.call(['ssh','-i','/home/ksuryanarayanan/bbops_id_dsa',i,'ls -lrt /root/kartiktest'])
 subprocess.call(['ssh','-i','/home/ksuryanarayanan/bbops_id_dsa',i,'find /root/kartiktest -name webconfigure.properties.pre.test -exec sed -i "s/prelay502.rly5.blackberry:1521:PRLY502/(DESCRIPTION=(ADDRESS_LIST=(ADDRESS = (PROTOCOL = TCP)(HOST = s5-rya12.rly5.blackberry)(PORT = 1521))(ADDRESS = (PROTOCOL = TCP)(HOST = s5-ryb12.rly5.blackberry)(PORT = 1521))(ADDRESS=(PROTOCOL = TCP)(HOST = s6-rya12.rly6.blackberry)(PORT = 1521))(ADDRESS = (PROTOCOL = TCP)(HOST = s6-ryb12.rly6.blackberry)(PORT = 1521)))(ENABLE = BROKEN)(CONNECT_DATA =   (SERVER = DEDICATED)(SERVICE_NAME = PRLY502)))/" {} \;'])
f.close()
  
