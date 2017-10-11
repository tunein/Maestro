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
EVENT_TYPES = lambda_config.EVENT_TYPES

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

def check_s3():
  if 'trigger' in json_parser():
    invoke_source = json_parser()['trigger']['source']
  elif ARGS.invoke_method and ARGS.invoke_source:
    invoke_source = ARGS.invoke_source

  bucket_name = invoke_source
  try:
    s3.meta.client.head_bucket(Bucket=bucket_name)
    print("Bucket found!")
    return True
  except ClientError as error:
    print(error.response['Error']['Message'])
    sys.exit(1)

def get_sns_arn():
  if 'trigger' in json_parser():
    invoke_source = json_parser()['trigger']['source']
  elif ARGS.invoke_method and ARGS.invoke_source:
    invoke_source = ARGS.invoke_source

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
      if topic_name in item:
        return item

  except ClientError as error:
    print(json.dumps(error.response, indent=4))

def get_cloudwatch_arn():
  if 'trigger' in json_parser():
    invoke_source = json_parser()['trigger']['source']
  elif ARGS.invoke_method and ARGS.invoke_source:
    invoke_source = ARGS.invoke_source

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

  if 'trigger' in json_parser():
    invoke_method = json_parser()['trigger']['method']
    invoke_source = json_parser()['trigger']['source']
  elif ARGS.invoke_method and ARGS.invoke_source:
    invoke_method = ARGS.invoke_method
    invoke_source = ARGS.invoke_source
  else:
    invoke_method = input("Enter an invocation method (s3/sns/cloudwatch): ")
    invoke_source = input("Enter an invocation source (bucket name/topic name/event name: ")

  if invoke_method in principals:
    if invoke_method == 's3':
      if check_s3():
        principal = 's3.amazonaws.com'
        print('Using principal: %s' % principal)
        source_arn = 'arn:aws:s3:::%s' % invoke_source
        print('Invoke source arn: %s' % source_arn)
    if invoke_method == 'sns':
      principal = 'sns.amazonaws.com'
      source_arn = get_sns_arn()
    if invoke_method == 'cloudwatch':
      principal = 'events.amazonaws.com'
      source_arn = get_cloudwatch_arn()

    if len(principal)>0:
      if len(source_arn)>0:

        if 'alias' in json_parser()['initializers']:
          qualifier = json_parser()['initializers']['alias']
        elif ARGS.alias:
          qualifier = ARGS.alias
        else:
          qualifier = ''

        statement_id = "%s-%s-%s" % (lambda_name, ARGS.alias, invoke_source)        

        if ARGS.dry_run:
          print(color.PURPLE + "***Dry Run option enabled***" + color.END)
          print(color.PURPLE + "Would add permissions for the following:" + color.END)
          print(color.PURPLE + "Action: 'lambda:InvokeFunction'" + color.END)
          print(color.PURPLE + "Function Name: %s" % lambda_name + color.END)
          print(color.PURPLE + "Principal: %s" % principal + color.END)
          print(color.PURPLE + "SourceArn: %s" % source_arn + color.END)
          print(color.PURPLE + "StatementId: %s" % statement_id + color.END)
          print(color.PURPLE + "Qualifier: %s" % qualifier + color.END)
          return True
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
  
  if 'alias' in json_parser()['initializers']:
    alias = ':%s' % json_parser()['initializers']['alias']
  elif ARGS.alias:
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

    if 'trigger' in json_parser():
      invoke_method = json_parser()['trigger']['method']
      invoke_source = json_parser()['trigger']['source']
    elif ARGS.invoke_method and ARGS.invoke_source:
      invoke_method = ARGS.invoke_method
      invoke_source = ARGS.invoke_source
    else:
      invoke_method = input("Enter an invocation method (s3/sns/cloudwatch): ")
      invoke_source = input("Enter an invocation source (bucket name/topic name/event name: ")

    if invoke_method == 's3':
      bucket_name = invoke_source
      bucket_notification = s3.BucketNotification(bucket_name)

      if ARGS.dry_run:
        print(color.PURPLE + "***Dry Run option enabled***" + color.END)
        print(color.PURPLE + "Would add invocation permissions for the following:" + color.END)
        print(color.PURPLE + "Lambda: %s" % lambda_name + color.END)
        print(color.PURPLE + "Bucket: %s" % bucket_name + color.END)
        print(color.PURPLE + "Event: s3:ObjectCreated:*" + color.END)
        return True
      else:
        try:
          e_type = "ObjectCreated"

          if 'trigger' in json_parser():
            if 'event_type' in json_parser()['trigger']:
              event_type = json_parser()['trigger']['event_type']
            else:
              event_type = e_type
          elif ARGS.event_type:
            event_type = ARGS.event_type
          else:
            event_type = e_type

            if event_type in EVENT_TYPES:
              e_type = event_type
            else:
              print("Event type invalid, removing permissions and rolling back")
              return False

          put = bucket_notification.put(
                    NotificationConfiguration={'LambdaFunctionConfigurations': [
                    {
                      'LambdaFunctionArn': '%s%s' % (arn, alias),
                      'Events': [
                          's3:%s:*' % e_type,
                          ],
                    }
                  ]
                }
              )
          if put['ResponseMetadata']['HTTPStatusCode'] == 200:
            print("Permssions granted, linked to %s on %s as Lambda invocator" % (invoke_source, invoke_method))
            return True
        except ClientError as error:
          print(json.dumps(error.response, indent=4))
          return False

    if invoke_method == 'sns':
      topic_arn = get_sns_arn()

      if ARGS.dry_run:
        print(color.PURPLE + "***Dry Run option enabled***" + color.END)
        print(color.PURPLE + "Would add invocation permissions for the following:" + color.END)
        print(color.PURPLE + "TopicArn: %s" % topic_arn + color.END)
        print(color.PURPLE + "Protocol: Lambda" + color.END)
        print(color.PURPLE + "Endpoint: %s" % arn + color.END)
        return True
      else:
        try:
          subscription = sns_client.subscribe(
                          TopicArn=topic_arn,
                          Protocol='Lambda',
                          Endpoint='%s%s' % (arn, alias)
                        )
          if subscription['ResponseMetadata']['HTTPStatusCode'] == 200:
            print("Permssions granted, linked to %s on %s as Lambda invocator" % (invoke_source, invoke_method))
            return True
        except ClientError as Error:
          print(error.response['Error']['Message'])
          sys.exit[1]

    if invoke_method == 'cloudwatch':
      rule = invoke_source

      if ARGS.dry_run:
        print(color.PURPLE + "***Dry Run option enabled***" + color.END)
        print(color.PURPLE + "Would add invocation permissions for the following:" + color.END)
        print(color.PURPLE + "Cloudwatch Rule: %s" % rule + color.END)
        print(color.PURPLE + "ID: %s" % lambda_name + color.END)
        print(color.PURPLE + "Arn: %s" % arn + color.END)
        return True
      else:
        try:
          add_target = cloudwatch_client.put_targets(
                        Rule=rule,
                        Targets=[
                          {
                          'Id': lambda_name,
                          'Arn': '%s%s' % (arn, alias),
                          }
                        ]
                      )
          if add_target['ResponseMetadata']['HTTPStatusCode'] == 200:
            print("Permssions granted, linked to %s on %s as Lambda invocator" % (invoke_source, invoke_method))
            return True
        except ClientError as error:
          print(error.response['Error']['Message'])

def creation():
  if add_invoke_permission():
    if invoke_action():    
      return True
    else:
      if remove_invoke_action():
        return False 
  else:
    print("Permissions not granted, see error code")

def remove_invoke_action():
  lambda_name = json_parser()['initializers']['name'] 
  
  if 'trigger' in json_parser():
    invoke_source = json_parser()['trigger']['source']
  elif ARGS.invoke_method and ARGS.invoke_source:
    invoke_source = ARGS.invoke_source

  if 'alias' in json_parser()['initializers']:
    qualifier = json_parser()['initializers']['alias']
  elif ARGS.alias:
    qualifier = ARGS.alias
  else:
    qualifier = ''

  statement_id = "%s-%s-%s" % (lambda_name, ARGS.alias, invoke_source)

  try:
    remove = client.remove_permission(
                FunctionName=lambda_name,
                StatementId=statement_id,
                Qualifier=qualifier
            )
    if remove['ResponseMetadata']['HTTPStatusCode'] == 204:
      print("Successfully removed access permission on %s" % lambda_name)
      return True
  except ClientError as error:
    print(error.response['Error']['Message'])