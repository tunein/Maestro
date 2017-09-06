#!/usr/bin/env python2.7

import boto3
import maestro.lambda_config as lambda_config
import sys
import json
import os

DOC = sys.argv[2]

def json_parser():
  with open('%s' % DOC) as json_data:
    read = json.load(json_data)
    return read
    return True
  print("No json document to read.. Please enter a valid json document")

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
    print("Couldn't find the ID for your vpc, check the name and try again")
    return False

def get_subnets():
  filters = [{'Name': 'tag:Network', 'Values':['private']},{'Name': 'tag:Environment', 'Values':['%s' % json_parser()['environment']['environment']]}]
  vpc = ec2.Vpc(get_vpc_id())
  subnets = list(vpc.subnets.filter(Filters=filters))
  ids = []
  for subnet in subnets:
    if subnet.id != 0:
      ids.append(subnet.id)
  return ids

def main():
  if get_vpc_id():
    return get_subnets()

if __name__ == "__main__":
  main()