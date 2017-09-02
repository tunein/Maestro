#!/usr/bin/env python2.7

import boto3
import lambda_config
import sys
import json
import zipfile
import os
from botocore.exceptions import ClientError

DOC = sys.argv[2]
client = boto3.client('lambda')
iam = boto3.resource('iam')
roles = boto3.client('iam')

def json_parser():
  with open('%s' % DOC) as json_data:
    read = json.load(json_data)
    return read
    return True
  print "No json document to read.. Please enter a valid json document"

def alias_creation():
  lambda_name = json_parser()["initializers"]["name"]

  get_alias_name = raw_input("What would you like this alias to be called? ")
  alias_name = get_alias_name.lower()

  versions = client.list_versions_by_function(
                    FunctionName='%s' % lambda_name,
                  )

  version_json = json.dumps(versions, indent=4)
  load_json = json.loads(version_json)
  versions = load_json['Versions']
  avail_versions = []

  for version in versions:
    if version['Version'] != 0:
      print('version: %s' % version['Version'])
      avail_versions.append(version['Version'])

  function_version = raw_input("What version would you like to create an alias for? ")
  
  if function_version in avail_versions: 
    try:
      add_alias = client.create_alias(
        FunctionName='%s' % lambda_name,
        Name='%s' % alias_name,
        FunctionVersion='%s' % function_version,
      )
      print "Adding alias '%s' to lambda '%s' version '%s'" % (alias_name, lambda_name, function_version)
      return True
    except ClientError, message:
      print message
  else:
    print "I can't find that version, check list and find again"

alias_creation()