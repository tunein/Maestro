#!/usr/bin/env python2.7

import boto3
import lambda_config
import sys
import json
import zipfile
import os
import datetime
from botocore.exceptions import ClientError

s3 = boto3.resource('s3')
client = boto3.client('s3')
accepted_prompt_actions = ['y', 'n']
REGIONS = lambda_config.REGIONS
ACL_ANSWERS = lambda_config.ACL_ANSWERS
DOC = sys.argv[1]

def json_parser():
  with open('%s' % DOC) as json_data:
    read = json.load(json_data)
    return read
    return True
  print "No json document to read.. Please enter a valid json document"

def check_file():
  lambda_name = json_parser()["initializers"]["name"]
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
    prompt = raw_input("Bucket '%s' does not exist would you like to create? 'y/n': " % bucket_name)
    if prompt in accepted_prompt_actions:
      if prompt == 'y':
        if create_bucket():
          return True
      else:
        print "Exiting..."
        return False
    
def create_bucket():
  bucket_name = json_parser()['backup']['bucket_name']
  acl = raw_input("Give your bucket an ACL (Accepted answers: 'private', 'public-read', 'public-read-write', 'authenticated-read'): ")
  
  if acl in ACL_ANSWERS:
    bucket_location = raw_input("What region would you like to put the bucket in? ")
    if bucket_location.lower() in REGIONS:
      role = json_parser()["initializers"]["role"]

      create = client.create_bucket(
        ACL=acl,
        Bucket='%s' % bucket_name,
        CreateBucketConfiguration={
            'LocationConstraint': '%s' % bucket_location
        }
      )
      return True
      print "Creating bucket"
    print "Invalid region"
    return False
  print "Invalid ACL"
  return False

def upload_file():
  lambda_name = json_parser()["initializers"]["name"]
  bucket_name = json_parser()['backup']['bucket_name']
  file = os.getcwd() + '/%s.zip' % lambda_name
  filename = '%s.zip' % lambda_name
  if check_file():
    upload = s3.Bucket(bucket_name).upload_file(file, filename)
    print "Uploading file"
    return True
  else:
    print "Hmm... I couldn't find the file"
    return False

def check_upload_exists():
  lambda_name = json_parser()["initializers"]["name"]
  bucket_name = json_parser()['backup']['bucket_name']
  filename = '/%s.zip' % lambda_name
  file = s3.Object(bucket_name, filename)
  if file.key == filename:
    print "File exists"
    return True
  else:
    print "No file found in %s" % bucket_name
    return False

def main():
  if json_parser():
    if check_file():
      if check_s3():
        if upload_file():
          if check_upload_exists():
            print "Successfully backed up to s3"
  
if __name__ == "__main__":
  main()

'''
Keeping this around for later...

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")
'''
