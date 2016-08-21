#!/bin/env python
'''
Functions defined herein, calculates the Floating IP subnet utilization levels across the various tenants and gives you first hand information
into the availability of IP addresses for use.
'''
import subprocess
import json
# netaddr enables enables computations on IP Addresses which are otherwise treated as string objects.
from netaddr import *
import pprint
import ast
from collections import OrderedDict
from os import environ


def totalips_in_subnet(subnet_list):
    '''
    Function that calculates the total floating IPs that could be used for a specific floating IP network.
    Input to the function is a list of subnet(s) UUIDs, func loops through the list and returns the total number of IPs
    '''
    total_ips = 0
    for subnet in subnet_list:
        cmd = "neutron subnet-show " + subnet + " -f json"
        try:
            out = json.loads(subprocess.check_output(cmd, shell=True))
        except subprocess.CalledProcessError:
            continue
        try:
            subnet_start_ip = IPAddress(json.loads(out['allocation_pools'])["start"])
            subnet_end_ip = IPAddress(json.loads(out["allocation_pools"])["end"])
            total_ips = total_ips + int(subnet_end_ip - subnet_start_ip)
        except ValueError:
            #example a subnet may allocate IPs from 16-32 and then start from 36 to 254
            #Example: u'{"start": "10.30.128.36", "end": "10.30.135.254"}\n{"start": "10.30.128.16", "end": "10.30.128.32"}'

            subsections = out['allocation_pools'].split('\n')
            for sub in subsections:
                end_ip = IPAddress(ast.literal_eval(sub)['end'])
                start_ip = IPAddress(ast.literal_eval(sub)['start'])
                total_ips = total_ips + int(end_ip - start_ip)
    return total_ips

def allocated_ips_subnet(subnet_list):
    '''func that figures out the number of active floating IPs in use for a floating IP network'''

    #a different command that get the list of ports and their associated IPs. Populate the data from the command in a list object.
    cmd1 = "neutron port-list  -F fixed_ips -f json"

    #Load the json data as a dictionary object
    neutron_port_list = json.loads(subprocess.check_output(cmd1, shell=True))


    #Grab & Work only with relevant fields which will be the subnet UUID and the IP alongside it
    allusedip_listing = []
    for i in neutron_port_list:
        for j in i['fixed_ips'].split('\n'):
            allusedip_listing.append(ast.literal_eval(j))   #ast.literal_eval is used to evaluate the string as a key-value pair

    count_ips_used = 0
    for subnet in subnet_list:
        count_ips_used += len(filter(lambda subnetname: subnetname['subnet_id'] == subnet, allusedip_listing))
    return count_ips_used

def execute():
    # cmd that gets the list of external i.e floating IP networks
    cmd = 'neutron net-external-list -f json'

    #get all data about floating-external-list networks
    floating_nets = json.loads(subprocess.check_output(cmd, shell=True))

    # Here is the actual data structure that will be populated for the floating networks.
    floating_net_data = OrderedDict([])

    # start populating the OrderedDict with values for each floating IP network
    # For every external network, a dict of values are added which are subnet UUIDs, subnet CIDRs, # of IPs from all subnets.
    for net in floating_nets:
        floating_net_data[net['name']] = {}
        subnetid_list = []
        subnetcidr_list = []
        for subnet in net['subnets'].split('\n'):
            subnetid_list.append(subnet.split(' ')[0].rstrip())
            subnetcidr_list.append(subnet.split(' ')[1].rstrip())
        floating_net_data[net['name']]['subnets_id'] = subnetid_list
        floating_net_data[net['name']]['subnets_cidr'] = subnetcidr_list
        floating_net_data[net['name']]['numips_in_net'] = totalips_in_subnet(subnetid_list)
        floating_net_data[net['name']]['count_ips_used'] = allocated_ips_subnet(subnetid_list)

    #Loop through each floating IP network and print the details for the same
    for x in floating_net_data.iteritems():
        pprint.pprint(x)
        print
