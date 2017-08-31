#!/usr/bin/env python2.7

import boto3
import lambda_config
import sys
import json
import os

DOC = sys.argv[1]

def json_parser():
  with open('%s' % DOC) as json_data:
    read = json.load(json_data)
    return read
    return True
  print "No json document to read.. Please enter a valid json document"

ec2 = boto3.resource('ec2', region_name='%s' % json_parser()['initializers']['region'])
client = boto3.client('ec2')

def get_vpc_id():
  filters = [{'Name': 'tag:Name', 'Values':['%s' % json_parser()['vpcconfig']['vpc_name']]}]
  vpcs = list(ec2.vpcs.filter(Filters=filters))
  for vpc in vpcs:
    response = client.describe_vpcs(
      VpcIds=[
        vpc.id,
      ]
    )
    vpc_id = response['Vpcs'][0]['VpcId']
    if len(vpc_id)!=0:
      return vpc_id
    print "Couldn't find the ID for your vpc, check the name and try again"
    return False

def get_subnets():
  vpc = ec2.Vpc(get_vpc_id())
  subnets = vpc.subnets.all()
  for subnet in subnets:
    print subnet.id

get_subnets()

#print get_vpc_id()

