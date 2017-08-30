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

lambda_name = 'test'
DOC = sys.argv[1]

def json_parser():
  with open('%s' % DOC) as json_data:
    read = json.load(json_data)
    return read
    return True
  print "No json document to read.. Please enter a valid json document"

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

def check_file():
  file_path = os.getcwd() + '/%s.zip' % lambda_name
  if os.path.exists(file_path):
    return True
  return False

def check_s3():
  bucket_name = json_parser()['backup']['bucket_name']
  list_buckets = client.list_buckets()
  response = json.dumps(list_buckets, default=datetime_handler, indent=4)
  load_response = json.loads(response)

  for buckets in load_response['Buckets']:
    print buckets['Name']
'''
    if any(name in bucket_name for name in current_buckets):
      return 
    else:
      raw_input("Bucket does not exist would you like to create? 'y/n': ")
'''
def create_bucket():
  return "create bucket"

def upload_file():
  return "upload object here"

check_s3()
