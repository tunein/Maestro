#Import external libs
import boto3
import sys
import json
import os
from botocore.exceptions import ClientError

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

def get_vpc_id(vpc_name):
    '''
    Gets the unique ID of the given VPC by AWS and returns it

    ex: vpc-a1b2c4d4

    args: 
      vpc_name: name of the vpc 
    '''
    filters = [{'Name': 'tag:Name', 'Values': ['%s' % vpc_name]}]
    vpcs = list(ec2.vpcs.filter(Filters=filters))
    for vpc in vpcs:
        try:
            response = client.describe_vpcs(
              VpcIds=[
                vpc.id,
              ]
            )
            vpc_id = response['Vpcs'][0]['VpcId']
            if len(vpc_id)!=0:
                return vpc_id
            else:
                print(color.RED + "Couldn't find the ID for your vpc, check the name and try again" + color.END)
                return False
        except ClientError as error:
            print(color.RED + error.response['Error']['Message'] + color.END)  

def get_subnets(vpc_id):
    '''
    Takes the ID from "get_vpc_id" and gathers all private subnets 
    then it puts them in a list and returns them for the lambda config

    args:
      vpc_id: the unique ID given to the VPC by aws
    '''
    vpc = ec2.Vpc(vpc_id)
    subnets = list(vpc.subnets.all())

    ids = {}
    list_id = []

    for subnet in subnets:
        try:
            info = ec2.Subnet(subnet.id)
            get_tags = list(info.tags)
            dumper = json.dumps(get_tags, indent=4)
            loader = json.loads(dumper)

            for item in loader:
                private_tag = item['Value']

                if 'private' in private_tag:
                    ids.update({private_tag: subnet.id})
        except ClientError as error:
            print(color.RED + error.response['Error']['Message'] + color.END)

    for key, value in ids.items():
        list_id.append(value)

    return list_id

def main(vpc_name):
    '''
    Main entry point of this module, for simplicities sake

    args:
      vpc_name: taken from the config
    '''
    vpc_id = get_vpc_id(vpc_name)
    return get_subnets(vpc_id)