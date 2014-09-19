#!/usr/local/bin/python
'''
A script which was written to perform audit of hosts to make sure they have standard setup in place to conform to standard monitoring and configuration management requirements of the organization.
Scripts arguments are input of IPs in a file and DC number when calling the script. Output of the results of audit are redirected to a csv file.

Script uses Boolean values to capture the success/failure of a check. it alsoemploys SSH key to be added automatically as the script runs through a chunk of hosts

Example output: argument file has 1 ip, DC number is 11 for which compliance has to be checked. First part is the verbose output as script executes and the second is fetched from the file where the results were written.
[root@spider10001 python]# ./basic_check2.py ips.txt 11
Host is up & running
Warning: Permanently added '192.168.46.90' (RSA) to the list of known hosts.
Puppet agent is running
Sysedge agent is running
Trap destinations are fine
192.168.46.90 is in Smarts
['wis-mom11021b.mon11.blackberry.', True, True, True, True, True, ['STRING: "crond"', 'STRING: "ntpd"', 'STRING: "sshd"', 'STRING: "syslogd"', 'STRING: "cron"'], (True, '31')]
[root@spider10001 python]# tail -1 stats.csv
wis-mom11021b.mon11.blackberry.,True,True,True,True,True,"['STRING: ""crond""', 'STRING: ""ntpd""', 'STRING: ""sshd""', 'STRING: ""syslogd""', 'STRING: ""cron""']","(True, '31')"

'''
import subprocess
import shlex
import os
import csv
import sys

# Trap receivers of SNMP traps are DC specific & according to the DC argument provided, the hosts will be validated against these values.
dc = sys.argv[2]
if dc == '2':
    trapd = ['192.168.26.230','fm-dn01a.c0.mon2.blackberry','192.168.26.231','fm-dn01b.c0.mon2.blackberry','172.25.185.242','fm-sn01a.c0.mon2.blackberry','172.25.185.243','fm-sn01b.c0.mon2.blackberry']
elif dc == '4':
    trapd = ['192.168.29.230','bm-dn01a.mon4.blackberry','192.168.29.231','bm-dn01b.mon4.blackberry','172.26.185.242','bm-sn01a.mon4.blackberry','172.26.185.243','bm-sn01b.mon4.blackberry']
elif dc == '5':
    trapd = ['192.168.32.210','montraps5001a.mgmt5.blackberry','192.168.32.211','montraps5001b.mgmt5.blackberry']
elif dc == '6':
    trapd = ['192.168.35.210','montraps6001a.mgmt6.blackberry','192.168.35.211','montraps6001b.mgmt6.blackberry']
elif dc == '7':
    trapd = ['192.168.38.230','dn7001a.mgmt7.blackberry','192.168.38.231','dn7001b.mgmt7.blackberry','172.18.185.242','sn7001a.mon7.blackberry','172.18.185.243','sn7001b.mon7.blackberry']
elif dc == '10':
    trapd = ['192.168.49.22','montraps10001a.mon10.blackberry','192.168.49.23','montraps10001b.mon10.blackberry']
elif dc == '11':
    trapd = ['192.168.46.28','montraps11001a.mon11.blackberry','192.168.46.29','montraps11001b.mon11.blackberry']
elif dc == '20':
    trapd = ['192.168.43.149','montraps20001a.mon20.blackberry','192.168.43.150','montraps20001b.mon20.blackberry']
elif dc == '21':
    trapd = ['192.168.44.154','montraps21001a.mon21.blackberry','192.168.44.155','montraps21001b.mon21.blackberry']
else:
    print("DC not known")
    exit

#pingable = puppet_agent = sysedge_agent = sysedge_config = in_smarts = audit_config = in_ehealth = False

# as the name suggests this function checks if a host is pingable or not, use of Try/Except clauses to determine the same.
def pingcheck(ip):
    global pingable,puppet_agent,sysedge_agent,sysedge_config,in_smarts,audit_config,in_ehealth
    pingable = puppet_agent = sysedge_agent = sysedge_config = in_smarts = audit_config = in_ehealth = False
    cmd1 = 'ping -c 3 ' + ip

    try:
        cmd1op = subprocess.check_output(shlex.split(cmd1)).splitlines()[-2].find('0% packet loss')
        if cmd1op != -1:
              pingable = True
              print("Host is up & running")
        else:
              print("Host is not running")
        return pingable
    except subprocess.CalledProcessError:
      print("{} is not reachable").format(ip)
      return pingable

#Puppet agent running on the hosts is an important part of the audit, this function does that. 
def puppetagent(ip):
    global puppet_agent;puppet_agent = False
    cmd2 = 'ssh -i /home/ksuryanarayanan/bbops_id_dsa -o StrictHostKeyChecking=no ' + ip + ' "service puppet status"'
    try:
	cmd2op = subprocess.check_output(shlex.split(cmd2)).find('is running...')
    except subprocess.CalledProcessError:
	return puppet_agent
    if cmd2op != -1:
        puppet_agent = True
        print("Puppet agent is running")
    else:
        print("Puppet agent is not running")
    return puppet_agent

#Function to check if SNMP agent from vendor CA i.e sysedge is running on the host or not
def sysedgeagent(ip):
    global sysedge_agent;sysedge_agent = False
    cmd3 = 'ssh -i /home/ksuryanarayanan/bbops_id_dsa -o StrictHostKeyChecking=no ' + ip + ' "service sysedge status"'
    cmd3op = subprocess.check_output(shlex.split(cmd3)).find('SystemEDGE is running')
    if cmd3op != -1:
        sysedge_agent = True
        print("Sysedge agent is running")
    else:
        print("Sysedge agent is not running")
    return sysedge_agent

#Function to check if the SNMP agent is configured properly to redirect traps to the correct trap receiver hosts in that specific DC.
def sysedgeconfig(ip):
    global sysedge_config, trapd, dc
    sysedge_config = False
    cmd4 = 'ssh -i /home/ksuryanarayanan/bbops_id_dsa -o StrictHostKeyChecking=no ' + ip + ' "grep trap_community /etc/sysedge.cf | grep public"'
    cmd4op = subprocess.check_output(shlex.split(cmd4))
    if dc in ('2','4','7'):
        if ip[0:3] == '192':
            if cmd4op.splitlines()[0].split(" ")[2] in (trapd[0],trapd[1],trapd[2],trapd[3]) and cmd4op.splitlines()[1].split(" ")[2] in (trapd[0],trapd[1],trapd[2],trapd[3]):
                sysedge_config = True
                print("Trap destinations are fine")
            else:
                print("Trap destination are misconfigured")
        else:
            if cmd4op.splitlines()[0].split(" ")[2] in (trapd[4],trapd[5],trapd[6],trapd[7]) and cmd4op.splitlines()[1].split(" ")[2] in (trapd[4],trapd[5],trapd[6],trapd[7]):
                sysedge_config = True
                print("Trap destinations are fine")
            else:
                print("Trap destination are misconfigured")
    else:
        if cmd4op.splitlines()[0].split(" ")[2] in (trapd[0],trapd[1],trapd[2],trapd[3]) and cmd4op.splitlines()[1].split(" ")[2] in (trapd[0],trapd[1],trapd[2],trapd[3]):
            sysedge_config = True
            print("Trap destinations are fine")
        else:
            print("Trap destination are misconfigured")
    return sysedge_config

# Function to check if the system is being monitored in EMC Smarts or not, it utilises a call to another short script that checks this.
def smartscheck(ip):
    global in_smarts;in_smarts = False
    cmd5 = 'ssh -i /home/ksuryanarayanan/bbops_id_dsa gn11001a.mon11.blackberry "/opt/InCharge/SAM/smarts/bin/sm_perl /opt/smarts-scripts/findIP/findip.pl --ip=' + ip + ' --config=/opt/smarts-scripts/findIP/config.txt | grep exists " '
    try:
        cmd5op = subprocess.check_output(shlex.split(cmd5)).find('true')
    except subprocess.CalledProcessError:
        cmd5op = subprocess.check_output(shlex.split(cmd5)).find('true')
    if cmd5op != -1:
     in_smarts = True
     print("{} is in Smarts").format(ip)
    else:
     print("{} Not in Smarts").format(ip)
    return in_smarts

# Function to check if the hosts is under Auditron(an in house monitoring tool that takes care of process monitoring.
def auditron(ip):
    global audit_config;audit_config = False
    cmd6 = 'ssh -i /home/ksuryanarayanan/bbops_id_dsa jump11001a.mon11.blackberry "/home/tmyra/ops_tools/procmon/procmon-showall2.sh ' + ip + '"'
    cmd6op = subprocess.check_output(shlex.split(cmd6)).splitlines()
    return cmd6op

# Function to check if the host IP is being monitored in CA eHealth systems, basically meant for Hardware and Filesystems, partition monitoring. this is done by checking the mysql DB for existence of elements & getting a count of those elements for the host.
def ehealth(ip):
    global in_ehealth;in_ehealth = False
    cmd7 = 'mysql -h miscdb5001a.mgmt5.blackberry -u \'EhAutomation\' -p\'EhAutomation\' EhealthAutomation --skip-column-names -e "select count(name) from ElementsDatabase where ipAddr like \'' + ip + ':%\';"'
    cmd7op = subprocess.check_output(shlex.split(cmd7)).strip()
    if cmd7op == '0':
        print('{} is not in Ehealth').format(ip)
    else:
        in_ehealth = True
    return in_ehealth,cmd7op

#Run throught the list of IPs from the input file one by one and output the output to a csv file. If the hosts itself is down, there is no need to run through the other checks.
iplist = sys.argv[1]
with open(iplist,'r') as file:
        for ip in file.readlines():
	    ip_stat = []
	    hostcmd = 'dig -x ' + ip + ' +short'
	    hostname = subprocess.check_output(shlex.split(hostcmd)).strip()
	    ip_stat.append(hostname)	
            pingable = pingcheck(ip.strip())
            if pingable == False:
                ip_stat.append(pingable)
                ip_stat.append(puppet_agent)
                ip_stat.append(sysedge_agent)
                ip_stat.append(sysedge_config)
                ip_stat.append(in_smarts)
                ip_stat.append(audit_config)
		ip_stat.append(in_ehealth)
		print ip_stat
                with open('stats.csv','ab') as myfile:
                  myfilewriter = csv.writer(myfile)
                  myfilewriter.writerow(ip_stat)
            else:
                ip_stat.append(pingable)
                ip_stat.append(puppetagent(ip.strip()))
                ip_stat.append(sysedgeagent(ip.strip()))
                ip_stat.append(sysedgeconfig(ip.strip()))
                ip_stat.append(smartscheck(ip.strip()))
                ip_stat.append(auditron(ip.strip()))
		ip_stat.append(ehealth(ip.strip()))
                print ip_stat
                with open('stats.csv','ab') as myfile:
                  myfilewriter = csv.writer(myfile)
                  myfilewriter.writerow(ip_stat)
