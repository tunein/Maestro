import boto3
import maestro.lambda_config as lambda_config
import sys
import json
import os
from botocore.exceptions import ClientError
from maestro.cli import ARGS

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
  print("No json document to read.. Please enter a valid json document")

ec2 = boto3.resource('ec2', region_name='%s' % json_parser()['initializers']['region'])
client = boto3.client('ec2')

def get_vpc_id():
  filters = [{'Name': 'tag:Name', 'Values': ['%s' % json_parser()['vpc_setting']['vpc_name']]}]
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

def get_subnets():
  vpc = ec2.Vpc(get_vpc_id())
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
        keys = item['Value']
        if keys.find('private')>0:
          ids.update({keys: subnet.id})
    except ClientError as error:
      print(color.RED + error.response['Error']['Message'] + color.END)

  for key, value in ids.items():
    list_id.append(value)

  return list_id

def main():
  if get_vpc_id():
    return get_subnets()

if __name__ == "__main__":
  main()
