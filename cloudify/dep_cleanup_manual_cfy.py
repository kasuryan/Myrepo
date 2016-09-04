#!/usr/bin/env python
'''
Name: dep_cleanup_manual_cfy.py

Purpose: Utility script for cleanup a deployment when the traditional teardown from cloudify UI fails, use it as a last
         resort option.
         We could easily modify it to accept a list of deployments for cleanup but such a use case doesn't exists
         and hence it accepts a single deployment ID.

 Input: Pass the CFY manager IP/hostname & the deployment ID as string


Author: Kartik Suryanarayanan
Date: 8/30/2016
Version: 1.0
'''
import subprocess
import paramiko
import getpass
from argparse import ArgumentParser

parser = ArgumentParser(description="Manual teardown of deployment when nothing else works, make sure any live nodes/instances are removed in the backend")
parser.add_argument('-t', '--management-ip', required=True, dest='mgmtip', help='CFY manager hostname or IP')
parser.add_argument('-d', '--deployment-id', required=True, dest='dep_id', help='Deployment ID i.e name')

args = parser.parse_args()


def del_elastic_data(mgmt_ip, dep_id):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        username = raw_input("Enter CFY manager ssh credentials, Username: ")
        passw = getpass.getpass("Enter password: ")
        # Connect to the cloudify atomic host.
        client.connect(mgmt_ip, username=username, password=passw)
        # Grab the container IP for the cloudify docker instance
        stdin, stdout, stderr = client.exec_command("docker inspect --format '{{ .NetworkSettings.IPAddress }}' cfy")
        container_ip = stdout.read().rstrip()
        # Command strings for cleanup actions against the docker container(which is cloudify instance)
        cmd_string = 'docker exec cfy bash -c "service celeryd-' + dep_id + ' stop; service celeryd-' + dep_id + '_workflows stop;rm -rf ~/cloudify.' + dep_id + ';rm -rf ~/cloudify.' + dep_id + '_workflows;rm -rf /etc/default/celeryd-'  + dep_id + '; rm -rf /etc/default/celeryd-' + dep_id + '_workflows"'
        stdin, stdout, stderr = client.exec_command(cmd_string)

        cmd1 = 'curl -XDELETE \'http://' + container_ip + ':9200/cloudify_storage/execution/_query?pretty\' -d \'{"query": {"term": {"deployment_id": "' + dep_id + '"}}}\''
        stdin, stdout, stderr = client.exec_command(cmd1)
        print stdout.read()

        cmd2 = 'curl -XDELETE \'http://' + container_ip + ':9200/cloudify_storage/node_instance/_query?pretty\' -d \'{"query": {"term": {"deployment_id": "' + dep_id + '"}}}\''
        stdin, stdout, stderr = client.exec_command(cmd2)
        print stdout.read()

        cmd3 = 'curl -XDELETE \'http://' + container_ip + ':9200/cloudify_storage/node/_query?pretty\' -d \'{"query": {"term": {"deployment_id": "' + dep_id + '"}}}\''
        stdin, stdout, stderr = client.exec_command(cmd3)
        print stdout.read()

        cmd4 = 'curl -XDELETE \'http://' + container_ip + ':9200/cloudify_storage/deployment/' + dep_id + '?pretty\' -d \'\''
        stdin, stdout, stderr = client.exec_command(cmd4)
        print stdout.read()

del_elastic_data(args.mgmtip, args.dep_id)
