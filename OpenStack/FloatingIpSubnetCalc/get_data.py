#!/bin/env python
'''
Script that gets you the active Floating IP subnet utilization levels across all your tenants in the cloud environment by importing the actual file 'floatingips'
which has all the relevant logic built into it. This script is intended to give you status so you could proactively add additional subnets to increase IP Addresses
availability for the various tenants.
This script first sets the OpenStack environment variables to be able to execute OS cli commands and get data and work on the same.
It's also setting the stdout to a file and that file is being sent over email to a set of recepients interested in receiving this data.
Example Run:
 $ ./get_data.py
Enter your OS horizon username: suryak2
Enter your OS horizon password:
'''
import os
import floatingips # imports the file which has the actual logic builtin
import sys
import smtplib
import time
from email.mime.text import MIMEText
import getpass

username = raw_input("Enter your OS horizon username: ")
password = getpass.getpass("Enter your OS horizon password: ") # allows to not relay back on screen what you type as password
os.environ['OS_AUTH_URL'] = '' # Here goes the OpenStack Horizon Auth URL, kept blank here
os.environ['OS_TENANT_ID'] = '' # Here goes the tenant UUID, kept blank here
os.environ['OS_TENANT_NAME'] = "admin"
os.environ['OS_USERNAME'] = username
os.environ['OS_PASSWORD'] = password
os.environ['OS_REGION_NAME'] = "RegionOne"

sys.stdout = open("output.txt", "w")
print "Setting Environment for getting data from cloud 0"
print
print "Data from Cloud 0"
floatingips.execute()

fp = open("output.txt", "rb")
msg = MIMEText(fp.read())
fp.close()

me = 'kartik.suryanarayanan@xyz.com'
to = [ 'name1.surname1@xyz.com', 'name2.surname2@xyz.com', 'name3.surname3@xyz.com' ]
#to = 'kartik.suryanarayanan@xyz.com'
msg['Subject'] = 'Active utilization of FIP subnets'
msg['From'] = me
msg['To'] = ", ".join(to)
#msg['To'] = to

s = smtplib.SMTP('relay.xyz.com')
s.sendmail( me, to, msg.as_string())
s.quit()
