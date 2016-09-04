#!/usr/bin/env python
'''
Name: cloudify_cleanup.py

Purpose: Utility script to get a list of torn down deployments from the Cloudify instance and try and delete them gracefully.
          This wont delete deployments that have executions running or actives nodes. Only properly
          torn down deployments will be cleaned up.

 Input: Pass the CFY manager IP/hostname


Author: Kartik Suryanarayanan
Date: 8/30/2016
Version: 1.0
'''
import sys
from argparse import ArgumentParser
from cloudify_rest_client import CloudifyClient
from cloudify_rest_client import exceptions
from pprint import pprint

parser = ArgumentParser(description="TornDown deployment cleanup on a cloudify manager instance")
parser.add_argument('-t', '--management-ip', required=True, dest='mgmtip', help='CFY manager hostname or IP')
args = parser.parse_args()
client = CloudifyClient(args.mgmtip)

def get_torndown_depl(client):
''' Takes the Cloudify rest client connection object as a parameter to the functions and generates a list of
    deployments in the torn down state.
'''
    torn_deployments = []
    deployments = client.deployments.list()
    for deployment in deployments:
        dep_states = set()
        for node in client.nodes.list(deployment_id=deployment.id):
            for node_instance in client.node_instances.list(deployment_id=deployment.id, node_name=node.id):
                dep_states.add(node_instance.state)
        try:
            if next(iter(dep_states)) == "deleted":
                torn_deployments.append(deployment.id)
        except StopIteration:
            pass
    return torn_deployments

def remove_dep(deployment_list, myclient):
''' This function takes in a list of deployments & the rest client connection object for cleanup/removal on the cloudify instance '''
    failed_dep_cleanup = {}
    for dep in deployment_list:
        try:
            myclient.deployments.delete(deployment_id=dep)
        except exceptions.CloudifyClientError as e:
            failed_dep_cleanup[dep] = e
    # Returns deployment names if any that couldn't be cleaned up, alongside noting down the reasons for the same(which is the exception message)
    if len(tempdict) > 0:
        print "The following deployments could not be deleted for reasons below"
        print
        pprint(failed_dep_cleanup.items())

print "Please wait while we fetch the deployments in torn down state as seen on Storm UI"
torn_dep_list = get_torndown_depl(client)
if len(torn_dep_list) == 0:
    print "No deployments found to be in torn down state on the cloudify instance"
    sys.exit()
print "Following {} deployments are in a teardown state and ready to be deleted/removed from Cloudify/Storm UI".format(str(len(torn_dep_list)))
print
for dep in torn_dep_list:
    print dep
inp = raw_input("Are you good to go ahead? press y/n: ")
if inp in ('y','Y'):
    remove_dep(torn_dep_list, client)
elif inp in ('n', 'N'):
    print "Exiting.."
    sys.exit()
else:
    print "Quitting, invalid input"
    sys.exit()
