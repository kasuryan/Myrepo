#!/usr/bin/python
'''
A script to generate java process stats: jstack threaddump, jstat output, jmap stats, top output capture. Then these files are zipped and send across in email to recipients 
for further analysis. This script was used by Services Operation Center folks to generate & capture stats for development team for them to assess what was happening on the server
at times of issues like say "Out of Memory situation within java application" 
'''
import os
import subprocess
import shlex
import sys
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from platform import node

hostname = node()

dump_path = "/tmp/javaStats/"

def jps():
        #subprocess.check_output('ps -ef | grep [a]utofsd | awk \'{print $2}\'', shell=True).splitlines()
        list_pid = subprocess.Popen('jps | grep Server | awk \'{print $1}\'', shell=True, stdout=subprocess.PIPE).communicate()[0].rstrip()
        return list_pid

def threaddump_jstack(jpid, dump_path):
        try:
                cmd = "for i in 1 2 3 4; do jstack -l " + jpid + " > " + dump_path + "jstack_out.${i}; sleep 5; done"
                subprocess.check_call(cmd, shell=True)
        except subprocess.CalledProcessError:
                print "Threaddump generation had an issue executing"


def top_output(dump_path):
        try:
                if not os.path.isdir(dump_path):
                        print "Creating a new directory " + dump_path
                        cmd = "mkdir " + dump_path
                        subprocess.check_call(cmd, shell=True)
                cmd1 = "top -bn1 > " + dump_path + "top_bn1"
                subprocess.check_call(cmd1, shell=True)
        except subprocess.CalledProcessError:
                print "Top command could not be run specifically."

def jstat(jpid, dump_path):
        try:
                #This example attaches to lvmid 21891 and takes 7 samples at 250 millisecond intervals and displays the output as specified by the -gcutil option.
                #jstat -gcutil 21891 250 7
                cmd = "jstat -gccause " + jpid + " 250 7 " + "> " + dump_path + "jstat_output"
                subprocess.check_call(cmd, shell=True)

        except subprocess.CalledProcessError:
                print "Jstat command could not be run."

def jmap(jpid, dump_path):
        try:
                cmd = "jmap -heap " + jpid + " > " + dump_path + "headpdump_output"
                subprocess.check_call(cmd, shell=True)
        except subprocess.CalledProcessError:
                print "Heapdump run had an issue"

def file_zip(dump_path):
        try:
                cmd = "cd " + dump_path + ";zip javastats.zip *"
                subprocess.check_call(cmd, shell=True)
        except subprocess.CalledProcessError:
                print "JavaStats File zip had an issue"

def send_mail(filename):
        send_from = 'kasuryan@sendgrid.me'
        send_to = 'kartik.suryanarayanan@autodesk.com'
        subject = hostname +':JavaStats & top output'
        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = send_to
        msg['Subject'] = subject
        msg.preamble = subject
        #msg.attach(MIMEText(text))

        with open(filename, "rb") as fil:
                msg.attach(MIMEApplication(
                        fil.read(),
                        Content_Disposition='attachment; filename="%s"' % basename(filename),
                        Name=basename(filename)
                    ))

        username = 'kasuryan'
        password = 'a360devops'
        server = smtplib.SMTP('smtp.sendgrid.net')
        server.ehlo()
        server.starttls()
        server.login(username,password)
        #You could add more recepients below in the array as needed separated by ','
        server.sendmail('kasuryan@sendgrid.me', ['kartik.suryanarayanan@autodesk.com'], msg.as_string())
        server.quit()


print "Script generates thread dumps using jstack, top output, jstat output"

jpid = jps()
if jpid == '':
        print "No java process found, EXITING!!!!"
        sys.exit(0)
top_output(dump_path)
jstat(jpid, dump_path)
jmap(jpid, dump_path)
threaddump_jstack(jpid, dump_path)
file_zip(dump_path)
send_mail("/tmp/javaStats/javastats.zip")


print "Script run successfully"
