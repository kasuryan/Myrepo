#!/usr/local/bin/python
'''
A script to get data from various hosts and use that data to output Puppet Class declarations that could be then used in the Node definitions.
Loop through a list of list of files, for each host get some specific data that will be required in the parameterized class declarations, We use nested dictionary maindict{} to hold a data dictionary "mydict" specific to each host and
later use the same data to output the class declarations specific to each host.
This script helps in reducing time having to login to each host and get the desired data and use them to manually create Puppet class declarations.
Example output, text replaced with "xxx" to protect information :
rlytelnet10001a.mon10.blackberry.

        class {'webconfig':
                dburl => '(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP) (HOST=xxxxxxxxxxxxxxxxxxx)(PORT=1521))(ADDRESS=(PROTOCOL=TCP)(HOST=xxxxxxxxxxxxxxxx) (PORT=1521)) (ADDRESS=(PROTOCOL=TCP) (HOST=xxxxxxxxxxxxxxxxxx)(PORT=1521)) (ADDRESS=(PROTOCOL=TCP) (HOST=xxxxxxxxxxxxxxxxxxxxxx)(PORT=1521)))(ENABLE=BROKEN)(CONNECT_DATA=(SERVER = DEDICATED)(SERVICE_NAME=PRLY100)))',
                rlydb_username => 'RelayWebConf01',
                rlydb_passwd => 'xxxxxxxx',
                rlycomponent_dsn => 'WEBCONFIG-RLYTELNET10001a',
                bindtoip =>'172.21.129.88',
        }
rlytelnet10001b.mon10.blackberry.

        class {'webconfig':
                dburl => '(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP) (HOST=xxxxxxxxxxxxxxxxxxxx)(PORT=1521))(ADDRESS=(PROTOCOL=TCP)(HOST=xxxxxxxxxxxxxxxxx) (PORT=1521)) (ADDRESS=(PROTOCOL=TCP) (HOST=xxxxxxxxxxxxxxxxxx)(PORT=1521)) (ADDRESS=(PROTOCOL=TCP) (HOST=xxxxxxxxxxxxxxxxxxxxx)(PORT=1521)))(ENABLE=BROKEN)(CONNECT_DATA=(SERVER = DEDICATED)(SERVICE_NAME=PRLY100)))',
                rlydb_username => 'RelayWebConf01',
                rlydb_passwd => 'xxxxxxxxx',
                rlycomponent_dsn => 'WEBCONFIG-RLYTELNET10001b',
                bindtoip =>'172.21.129.89',
        }
...... Output truncated.. 


'''
import subprocess
import shlex

maindict = {}
def getdata(hostname):
	global maindict
	mydict = {}
	cmd = 'ssh -i /home/ksuryanarayanan/bbops_id_dsa -o StrictHostKeyChecking=no ' + hostname + ' "find /usr/local/apache-tomcat/webapps/ -name webconfigure.properties -exec  grep -E \\"^(dburl|username|password|relaycomponent\.(dsn|BindToIP))\\" {} \;" '
	for i in subprocess.check_output(shlex.split(cmd)).splitlines():
		list = i.split("=",1)
		mydict[list[0]] = list[1]	
	mydict['dburl'] = mydict['dburl'][18:]
	maindict[hostname] = mydict

with open("webconfighosts","r") as f:
 for line in f.readlines():
	getdata(line)
	print line
	print "\tclass {" + "'webconfig': \n\t\tdburl => '{}', \n\t\trlydb_username => '{}', \n\t\trlydb_passwd => '{}', \n\t\trlycomponent_dsn => '{}', \n\t\tbindtoip =>'{}',".format(maindict[line]['dburl'],maindict[line]['username'],maindict[line]['password'],maindict[line]['relaycomponent.dsn'],maindict[line]['relaycomponent.BindToIP']) + "\n\t}"
