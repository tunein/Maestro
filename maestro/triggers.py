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

def json_parser():
  with open('%s' % DOC) as json_data:
    read = json.load(json_data)
    return read
    return True
  print("No json document to read.. Please enter a valid json document")

def get_s3_arn():
  print("Here is where we get the info for s3")

def get_sns_arn():
  print("Here is where we get the info for sns")

def get_sqs_arn():
  print("Here is where we get the info for sqs")

def get_cloudwatch_arn():
  print("Here is where we get the info for cloudwatch")

def get_aliases():
  print("Here is where you grab avail aliases")

def add_invoke_action():
  lambda_name = json_parser()['initializers']['name']

  if ARGS.invoke_method in principals:

    if ARGS.invoke_method == 's3':
      principal = 's3.amazonaws.com'
      source_arn = "%s/*" % get_s3_arn()
    if ARGS.invoke_method == 'sqs':
      principal = 'sqs.amazonaws.com'
      source_arn = get_sns_arn()
    if ARGS.invoke_method == 'sns':
      principal = 'sns.amazonaws.com'
      source_arn = get_sqs_arn()
    if ARGS.invoke_method == 'cloudwatch':
      principal = 'events.amazonaws.com'
      source_arn = get_cloudwatch_arn()

    if len(principal)>0:
      if len(source_arn)>0:
        statement_id = "%s-%s" % (lambda_name, json_parser['environment']['environment'])

        qualifier = get_aliases()

        try:
          add_permission = client.add_permission(
                            Action='lambda:InvokeFunction',
                            FunctionName=lambda_name,
                            Principle=principle,
                            SourceArn=source_arn,
                            StatementId=staement_id,
                            Qualifier=qualifer
                          )
          if add_permission['ResponseMetadata']['HTTPStatusCode'] == 201:
            print("Invoke permission added for ")
            return True
          else:
            return False
        except ClientError as error:
          print(error.response['Error']['Message'])

def remove_invoke_action():
  lambda_name = json_parser()['initializers']['name']


