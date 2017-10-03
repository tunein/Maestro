import boto3
import maestro.lambda_config as lambda_config
import sys
import json
import os
import datetime
from botocore.exceptions import ClientError
from maestro.cli import ARGS

ec2 = boto3.resource('ec2')
client = boto3.client('ec2')

DOC = ARGS.filename

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

def json_parser():
  with open('%s' % DOC) as json_data:
    read = json.load(json_data)
    return read
    return True
  print(color.RED + "No json document to read.. Please enter a valid json document" + color.END)

def security_groups():
  response = client.describe_security_groups()
  dump = json.dumps(response, indent=4)
  load = json.loads(dump)
  sgs = load['SecurityGroups']
  group_names = json_parser()['vpc_setting']['security_group_ids']

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