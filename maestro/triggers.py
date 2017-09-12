#!/usr/bin/env python3.6

import boto3
import lambda_config as lambda_config
import sys
import json
import os
from datetime import datetime
from botocore.exceptions import ClientError
#from maestro.cli import ARGS

#DOC = ARGS.filename
principals = lambda_config.PRINCIPALS

client = boto3.client('lambda')
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

my_session = boto3.session.Session()
region = my_session.region_name

accepted_prompt_actions = ['y', 'n']
REGIONS = lambda_config.REGIONS
ACL_ANSWERS = lambda_config.ACL_ANSWERS
'''
def json_parser():
  with open('%s' % DOC) as json_data:
    read = json.load(json_data)
    return read
    return True
  print("No json document to read.. Please enter a valid json document")
'''

invoke_method = 's3'
invoke_source = 'mm-img-bucket-test'

def check_s3():
  bucket_name = invoke_source #json_parser()['backup']['bucket_name']
  try:
    s3.meta.client.head_bucket(Bucket=bucket_name)
    return True
  except ClientError as error:
    print(error.response['Error']['Message'])
    sys.exit(1)
    
def get_s3_arn():
  if check_s3():
    print("Gathering ARN for S3 Bucket..")
    return "arn:aws:s3:::%s" % invoke_source

def get_sns_arn():
  print("Here is where we get the info for sns")

def get_sqs_arn():
  print("Here is where we get the info for sqs")

def get_cloudwatch_arn():
  print("Here is where we get the info for cloudwatch")

def get_aliases():
  print("Here is where you grab avail aliases")

def add_invoke_permission():
  lambda_name = 'example'

  if invoke_method in principals:

    if invoke_method == 's3':
      principal = 's3.amazonaws.com'
      source_arn = "%s/*" % get_s3_arn()
    if invoke_method == 'sqs':
      principal = 'sqs.amazonaws.com'
      source_arn = get_sns_arn()
    if invoke_method == 'sns':
      principal = 'sns.amazonaws.com'
      source_arn = get_sqs_arn()
    if invoke_method == 'cloudwatch':
      principal = 'events.amazonaws.com'
      source_arn = get_cloudwatch_arn()

    if len(principal)>0:
      if len(source_arn)>0:
        statement_id = "%s-%s" % (lambda_name, 'prod')#json_parser['environment']['environment'])
#        qualifier = get_aliases()

        try:
          add_permission = client.add_permission(
                            Action='lambda:InvokeFunction',
                            FunctionName=lambda_name,
                            Principal=principal,
                            SourceArn=source_arn,
                            StatementId=statement_id,
#                            Qualifier=qualifer
                          )
          if add_permission['ResponseMetadata']['HTTPStatusCode'] == 201:
            print("Invoke permission added for %s" % lambda_name)
            return True
          else:
            return False
        except ClientError as error:
          print(error.response['Error']['Message'])

def invoke_action():
  lambda_name = 'example'
  get_functions = client.list_functions()
  
  if get_functions['ResponseMetadata']['HTTPStatusCode'] == 200:
    dumper = json.dumps(get_functions, indent=4)
    loader = json.loads(dumper)
    functions = loader["Functions"]

    current_functions = []

    for function in functions:
      names = function['FunctionName']
      append = current_functions.append(names)

    if lambda_name in current_functions:
      arn = function['FunctionArn']
    else:
      print("No function found")
      return False

    if invoke_method == 's3':
      bucket_name = invoke_source
      bucket_notification = s3.BucketNotification(bucket_name)

      try:
        put = bucket_notification.put(
                  NotificationConfiguration={'LambdaFunctionConfigurations': [
                  {
                    'LambdaFunctionArn': '%s' % arn,
                    'Events': [
                        's3:ObjectCreated:*',
                        ],
                  }
                ]
              }
            )
      except ClientError as error:
        print(json.dumps(error.response, indent=4))

    if invoke_method == 'sns':
      print("Still figuring this out")

    if invoke_method == 'sqs':
      print("Still figuring this out")

    if invoke_method == 'cloudwatch':
      print("Still figuring this out")

def remove_invoke_action():
  lambda_name = json_parser()['initializers']['name']
  statement_id = "%s-%s" % (lambda_name, json_parser['environment']['environment'])
  qualifer = get_aliases()

  try:
    remove = client.remove_permission(
                FunctionName=lambda_name,
                StatementId=statement_id,
                Qualifier=qualifer
            )
    if remove['ResponseMetedata']['HTTPStatusCode'] == 201:
      print("Successfully removed access permission on %s" % lambda_name)
      return True
  except ClientError as error:
    print(error.response['Error']['Message'])