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

#placeholder while testing check_s3 function
check_s3()
    
def create_bucket():
  '''
  this function will create a bucket, driven by user input
  '''
	create = client.create_bucket(
			ACL='private'|'public-read'|'public-read-write'|'authenticated-read',
			Bucket='string',
			CreateBucketConfiguration={
					'LocationConstraint': 'EU'|'eu-west-1'|'us-west-1'|'us-west-2'|'ap-south-1'|'ap-southeast-1'|'ap-southeast-2'|'ap-northeast-1'|'sa-east-1'|'cn-north-1'|'eu-central-1'
			},
			GrantFullControl='string',
			GrantRead='string',
			GrantReadACP='string',
			GrantWrite='string',
			GrantWriteACP='string'
	)
  return "create bucket"

def upload_file():
  '''
  to do: figure out a way to show progress...
  '''
	bucket_name = = json_parser()['backup']['bucket_name']
	file = os.getcwd() + '/%s.zip' % lambda_name
	filename = '/%s.zip' % lambda_name
	if file.is_file():
		upload = client.Object(bucket_name, filename).upload_file(file)
  	print "Uploading file"
		return True
	else:
		print "Hmm... I couldn't find the file"
		return False

def check_upload_exists():
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
  '''
  this will be the main function that gets triggered to launch the rest
  '''
  return "main function!"
  
#if __name__ == "__main__":
#  main()

'''
Keeping this around for later...

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")
'''
