#External libs
import boto3
import sys
import json
import os
import datetime
from botocore.exceptions import ClientError

#Get our config
import maestro.config.lambda_config as lambda_config

#This is only here for printing pretty colors
class color:
     PURPLE = '\033[95m'
     CYAN = '\033[96m'
     DARKCYAN = '\033[36m'
     BLUE = '\033[94m'
     GREEN = '\033[92m'
     YELLOW = '\033[93m'
     RED = '\033[91m'
     BOLD = '\033[1m'
     UNDERLINE = '\033[4m'
     END = '\033[0m'

#Establish our boto resources
ec2 = boto3.resource('ec2')
client = boto3.client('ec2')

def security_groups(groups):
    '''
    Gets the unique security group ID for each named security group in config
    returns it in a list for reading by the main action modules

    args:
        groups: a list of security group names
    '''
    response = client.describe_security_groups()
    dump = json.dumps(response, indent=4)
    load = json.loads(dump)
    sgs = load['SecurityGroups']
    group_names = groups

    groups = {}

    for sg in sgs:
        groups.update({sg['GroupName']: sg['GroupId']})

    sg_ids = []

    for key, value in groups.items():
        if key in group_names: 
            sg_ids.append(value)

    if len(sg_ids) != 0:
        return sg_ids
    else:
        pass