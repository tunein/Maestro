import boto3
import maestro.lambda_config as lambda_config
import sys
import json
import os
import datetime
from botocore.exceptions import ClientError

ec2 = boto3.resource('ec2')
client = boto3.client('ec2')

DOC = sys.argv[2]

def json_parser():
  with open('%s' % DOC) as json_data:
    read = json.load(json_data)
    return read
    return True
  print("No json document to read.. Please enter a valid json document")

def security_groups():
  response = client.describe_security_groups()
  dump = json.dumps(response, indent=4)
  load = json.loads(dump)
  sgs = load['SecurityGroups']
  group_names = json_parser()['vpcconfig']['security_group_ids']

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

def main():
  return security_groups()

if __name__ == "__main__":
  main()