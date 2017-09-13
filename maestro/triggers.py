#!/usr/bin/env python3.6

import boto3
import maestro.lambda_config as lambda_config
import sys
import json
import os
from datetime import datetime
from botocore.exceptions import ClientError
from maestro.cli import ARGS

DOC = ARGS.filename
principals = lambda_config.PRINCIPALS

client = boto3.client('lambda')
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
sns_client = boto3.client('sns')
cloudwatch_client = boto3.client('events')

my_session = boto3.session.Session()
region = my_session.region_name

accepted_prompt_actions = ['y', 'n']
REGIONS = lambda_config.REGIONS
ACL_ANSWERS = lambda_config.ACL_ANSWERS
invoke_method = ARGS.invoke_method
invoke_source = ARGS.invoke_source

def json_parser():
  with open('%s' % DOC) as json_data:
    read = json.load(json_data)
    return read
    return True
  print("No json document to read.. Please enter a valid json document")

def check_s3():
  bucket_name = invoke_source
  try:
    s3.meta.client.head_bucket(Bucket=bucket_name)
    print("Bucket found!")
    return True
  except ClientError as error:
    print(error.response['Error']['Message'])
    sys.exit(1)

def get_sns_arn():
  topic_name = invoke_source
  list_of_topics = []
  try:
    existing_topics = sns_client.list_topics()
    dumper = json.dumps(existing_topics, indent=4)
    loader = json.loads(dumper)
    topics = loader['Topics']

    for obj in topics:
      for key, value in obj.items():
        list_of_topics.append(value)

    for item in list_of_topics:
      if item.find(topic_name):
        return item

  except ClientError as error:
    print(json.dumps(error.response, indent=4))

def get_cloudwatch_arn():
    event_name = invoke_source

    if len(event_name)>0:
      try:
        get_events = cloudwatch_client.list_rules(NamePrefix=event_name)
        
        dumper = json.dumps(get_events, indent=4)
        loader = json.loads(dumper)
        if loader['ResponseMetadata']['HTTPStatusCode'] == 200:
          rules = loader['Rules']
          for rule in rules:
              return rule['Arn']

      except ClientError as error:
        print(error.response['Error']['Message'])

def get_functions():
  lambda_name = json_parser()['initializers']['name']


def add_invoke_permission():
  lambda_name = json_parser()['initializers']['name']
  get_functions = client.list_functions()
  
  if get_functions['ResponseMetadata']['HTTPStatusCode'] == 200:
    dumper = json.dumps(get_functions, indent=4)
    loader = json.loads(dumper)
    functions = loader["Functions"]

    current_functions = {}

    for function in functions:
      names = function['FunctionName']
      arns = function['FunctionArn']
      append = current_functions.update({names: arns})

    dump_function_dict = json.dumps(current_functions, indent=4)
    load_function_dict = json.loads(dump_function_dict) 

    for key, value in current_functions.items():
      if key == lambda_name:
        arn = value

  if invoke_method in principals:
    if invoke_method == 's3':
      principal = 's3.amazonaws.com'
      print('principal: %s' % principal)
      source_arn = 'arn:aws:s3:::%s' % invoke_source
      print('arn: %s' % source_arn)
    if invoke_method == 'sns':
      principal = 'sns.amazonaws.com'
      source_arn = get_sns_arn()
    if invoke_method == 'cloudwatch':
      principal = 'events.amazonaws.com'
      source_arn = get_cloudwatch_arn()

    if len(principal)>0:
      if len(source_arn)>0:

        if ARGS.alias:
          qualifier = ARGS.alias
        else:
          qualifier = ''
        statement_id = "%s-%s" % (lambda_name, ARGS.alias)        

        try:
          add_permission = client.add_permission(
                            Action='lambda:InvokeFunction',
                            FunctionName=lambda_name,
                            Principal=principal,
                            SourceArn=source_arn,
                            StatementId=statement_id,
                            Qualifier=qualifier
                          )
          if add_permission['ResponseMetadata']['HTTPStatusCode'] == 201:
            print("Invoke permission added for %s" % lambda_name)
            return True
          else:
            return False
        except ClientError as error:
          print(error.response['Error']['Message'])

def invoke_action():
  lambda_name = json_parser()['initializers']['name']
  get_functions = client.list_functions()
  
  if ARGS.alias:
    alias = ':%s' % ARGS.alias
  else:
    alias = ''
  
  if get_functions['ResponseMetadata']['HTTPStatusCode'] == 200:
    dumper = json.dumps(get_functions, indent=4)
    loader = json.loads(dumper)
    functions = loader["Functions"]

    current_functions = {}

    for function in functions:
      names = function['FunctionName']
      arns = function['FunctionArn']
      append = current_functions.update({names: arns})

    dump_function_dict = json.dumps(current_functions, indent=4)
    load_function_dict = json.loads(dump_function_dict) 

    for key, value in current_functions.items():
      if key == lambda_name:
        arn = value

    if invoke_method == 's3':
      bucket_name = invoke_source
      bucket_notification = s3.BucketNotification(bucket_name)

      try:
        put = bucket_notification.put(
                  NotificationConfiguration={'LambdaFunctionConfigurations': [
                  {
                    'LambdaFunctionArn': '%s%s' % (arn, alias),
                    'Events': [
                        's3:ObjectCreated:*',
                        ],
                  }
                ]
              }
            )
        if put['ResponseMetadata']['HTTPStatusCode'] == 200:
          return True
      except ClientError as error:
        print(json.dumps(error.response, indent=4))

    if invoke_method == 'sns':
      topic_arn = get_sns_arn()
      try:
        subscription = sns_client.subscribe(
                        TopicArn=topic_arn,
                        Protocol='Lambda',
                        Endpoint=arn
                      )
        if subscription['ResponseMetadata']['HTTPStatusCode'] == 200:
          return True
      except ClientError as Error:
        print(error.response['Error']['Message'])
        sys.exit[1]

    if invoke_method == 'cloudwatch':
      rule = invoke_source
      try:
        add_target = cloudwatch_client.put_targets(
                      Rule=rule,
                      Targets=[
                        {
                        'Id': lambda_name,
                        'Arn': arn,
                        }
                      ]
                    )
        if add_target['ResponseMetadata']['HTTPStatusCode'] == 200:
          return True
      except ClientError as error:
        print(error.response['Error']['Message'])

def creation():
  if add_invoke_permission():
    if invoke_action():
      print("Permssions granted, linked to %s on %s as Lambda invocator" % (invoke_source, invoke_method))
      return True
    else:
      print("Actions not linked, see error code")
      return False 
  else:
    print("Permissions not granted, see error code")

def remove_invoke_action():
  lambda_name = json_parser()['initializers']['name']
  statement_id = "%s-%s" % (lambda_name, ARGS.alias)
  qualifier = ARGS.alias
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