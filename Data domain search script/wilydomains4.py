#!/usr/local/bin/python2.7
'''
Background & Goal of this script: We use Wily Application Performance Managament tool for Application monitoring. We had around 35+ number of wily instances sprawling in different DCs. Each wily instance hosted lots of different data domains
for segregating different application level metric data(See Wily Introscope Workstation.jpg in the folder for better understanding). During Incidents & troubleshooting we would be called upon to help with certain services.
It would be difficult to know on the top of our heads to remember which services are hosted under which Wily instances. This script addresses that bit and reduces the overhead.

The script utilizes a text file which has data in python dictionary format to provide the result instantaneously to avoid having to check remotely on each server. So whenever any user feels this dile data needs a refresh when seaching for a
data domain, he can pass on the keyword of the data domain as first argument and "refresh" keyword as the 2nd argument to ask it to fetch current data domains from all wily instance which will be fed into the file.

We had a naming convention in place for data domains in different regions. Adding to it a specific directory structure on wily servers that hosted these domains. The script utilizes this directory structure to figure out the data domains
hosted on each wily server.

The script can take two parameters, one is the search string that we use to determine where all a particular domain is hosted. the another argument we can use is "refresh" keyword which asks the script to fetch the latest data and not use the local data from the file. This will take longer than when not using the refresh keyword

Output with example: Here we are trying to determine where all(i.e wily instances) BISE data domains are hosted.
[root@spider10001 wilydomains]# ./wilydomains4.py bise
wis-mom21021a.mon21.blackberry
['KSA BISE 21']

wis-mom20021a.mon20.blackberry
['UAE BISE 20']

wis-mom5021a.mgmt5.blackberry
['US BISE5']

wis-mom9021a.mon9.blackberry
['CN BISE9']

wis-mom6021a.mgmt6.blackberry
['US BISE6']

wis-mom7021a.mgmt7.blackberry
['EMEA BISE7']

wis-mom6022a.mgmt6.blackberry
['US BISE6']

wis-mom10021a.mon10.blackberry
['AP BISE3']

wis-mom11021a.mon11.blackberry
['AP BISE3']


'''

import subprocess
import shlex
import re
import sys
import json

#Lists domains for a particular wismom host. this function returns a list of all domains hosted on a particular wily instance
def listdomains(wismom):
 wismom=wismom.strip()
 j=subprocess.check_output(['ssh', '-i', '/home/ksuryanarayanan/bbops_id_dsa', wismom, 'ls /opt/Introscope/config/modules/ | grep -v tar | grep -v .jar | grep -v tgz'])
 j=j.splitlines()
 return j

#Below function takes a list of wily instances that need to be queried for the domains they host and aggregates them into a dictionary data structure which is further output to a file.
def listall():
 f=open("wismom.txt")
 lines=f.read().splitlines()
 mydict = {} 
 for i in lines:
  mydict[i]=listdomains(i)
  f.close()
 open("wilydomains","w").close()
 json.dump(mydict, open("wilydomains","w"))

#Function that takes input as a search string to search for a wily domain from the data, search ignores case of the search sting

def search(sstring):
	myregex=r'(.*' + sstring + r'.*)'
	mydict = eval(open("wilydomains","r").read())
	for i in mydict:
 		m=[]
		j=mydict[i]
		for v in j:
		  ma = re.match(myregex,v,re.IGNORECASE)
  		  if ma:
    			m.append(ma.group())
		if len(m) > 0:
			print i
 			print m
			print

def refresh():
	global mydict
	mydict=listall()

#print mydict
#print str(sys.argv[1])
if len(sys.argv) > 2:
	if str(sys.argv[2]) == 'refresh':
		refresh()
	

searchstring=str(sys.argv[1])
search(searchstring)

