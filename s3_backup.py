#!/usr/bin/env python2.7

import boto3
import lambda_config
import sys
import json
import zipfile
import os
import datetime

s3 = boto3.resource('s3')
client = boto3.client('s3')
accepted_prompt_actions = ['y', 'n']

lambda_name = 'test'
DOC = sys.argv[1]

def json_parser():
  with open('%s' % DOC) as json_data:
    read = json.load(json_data)
    return read
    return True
  print "No json document to read.. Please enter a valid json document"

def check_file():
  file_path = os.getcwd() + '/%s.zip' % lambda_name
  if os.path.exists(file_path):
    return True
  return False

def check_s3():
  bucket_name = json_parser()['backup']['bucket_name']
  try:
    s3.meta.client.head_bucket(Bucket=bucket_name)
    return True
  except ClientError:
    prompt = raw_input("Bucket does not exist would you like to create? 'y/n': ")
    if prompt in accepted_prompt_actions:
      if prompt == 'y':
        print "Attempting to create new bucket"
        create_bucket()
      else:
        print "Exiting..."
        return False
    print "Not a valid response"

def create_bucket():
  return "create bucket"

def upload_file():
  return "upload object here"

check_s3()

'''
Keeping this around for later...

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")
'''
