#!/usr/bin/env python2.7

import boto3
import lambda_config
import sys
import json
import zipfile
import os

USER_ACTION = sys.argv[1]
DOC = sys.argv[2]
ACTION = USER_ACTION.lower()

client = boto3.client('lambda')
iam = boto3.resource('iam')
roles = boto3.client('iam')

AVAIL_RUNTIMES = lambda_config.AVAIL_RUNTIMES
AVAIL_ACTIONS = lambda_config.AVAIL_ACTIONS

def file_type():
  print "validating file type..."
  if len(DOC)>0:
    if DOC.lower().endswith('.json'):
      return True
    return False
  print "Please enter a valid json document after your action"

def json_parser():
  with open('%s' % DOC) as json_data:
    read = json.load(json_data)
    return read
    return True
  print "No json document to read.. Please enter a valid json document"

def validate_action():
  if json_parser()["initializers"]["name"]>0:
    if any(action in ACTION for action in AVAIL_ACTIONS):
      return True
    print "Not a valid action"
  print "Check your json document for the right syntax.."

def validate_runtime():
  if json_parser()["initializers"]["name"]>0:
    RUNTIME = json_parser()["provisioners"]["runtime"]
    print "validating runtime %s..." % RUNTIME
    if any(runtime in RUNTIME for runtime in AVAIL_RUNTIMES):
      return True
    print "Not a valid runtime"

def validate_role():
  name = json_parser()["initializers"]["role"]
  print "validating role %s..." % name
  data = iam.role_name=name
  if len(data)>0:
    return True
  print "invalid role"  

def validate_timeout():
  timeout = json_parser()["provisioners"]["timeout"]
  acceptable_range = range(1,301)
  if timeout in acceptable_range:
    return True
  print "Timeout should between between 1 and 300 seconds, please adjust"

def validation():
  if file_type():
    if json_parser():
      if validate_action():
        if validate_runtime():
          if validate_role():
            if validate_timeout():
              return True

def get_arn():
  role = iam.Role('%s' % json_parser()["initializers"]["role"])
  arn = role.arn
  return arn

def zip_folder():
  lambda_name = json_parser()["initializers"]["name"]
  output_path = os.getcwd() + '/%s.zip' % lambda_name
  folder_path = os.curdir + '/lambda'
  grab_lambda = os.walk(folder_path)
  length = len(folder_path)

  try:
    zipped_lambda = zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED)
    for root, folders, files in grab_lambda:
      for folder_name in folders:
        absolute_path = os.path.join(root, folder_name)
        shortened_path = os.path.join(root[length:], folder_name)
        print "Adding '%s' to package." % shortened_path
        zipped_lambda.write(absolute_path, shortened_path)
      for file_name in files:
        absolute_path = os.path.join(root, file_name)
        shortened_path = os.path.join(root[length:], file_name)
        print "Adding '%s' to package." % shortened_path
        zipped_lambda.write(absolute_path, shortened_path)
    print "'%s' lambda packaged successfully." % lambda_name
    return True
  except IOError, message:
    print message
    sys.exit(1)
  except OSError, message:
    print message
    sys.exit(1)
  except zipfile.BadZipfile, message:
    print message
    sys.exit(1)
  finally:
    zipped_lambda.close()

def check():
  proposed_function = json_parser()["initializers"]["name"]
  existing_functions = client.list_functions()
  parse = json.dumps(existing_functions)
  load = json.loads(parse)
  functions = load["Functions"]

  for function in functions:
    names = function.get("FunctionName")
    if any(name in proposed_function for name in names):
      return True
    else:
      return False

#Add commnad line args for dry run
#Add tags!
def create():
  lambda_name = json_parser()["initializers"]["name"]
  archive_name = os.getcwd() + '/%s.zip' % lambda_name
#  lambda_config = ''

  if zip_folder():
    print "Attempting to create lambda..."
    try:
      create = client.create_function(
        FunctionName='%s' % lambda_name,
        Runtime='%s' % json_parser()["provisioners"]["runtime"],
        Role='%s' % get_arn(),
        Handler='%s' % json_parser()["initializers"]["name"],
        Code={
          'ZipFile': open(archive_name, 'rb').read()
        },
        Description='%s' % json_parser()["initializers"]["description"],
        Timeout=json_parser()["provisioners"]["timeout"],
        MemorySize=json_parser()["provisioners"]["mem_size"]
        )
      return True
    except IOError, message:
      print message
      sys.exit(1)

#Add command line args for dry run & publish
def update():
  lambda_name = json_parser()["initializers"]["name"]
  archive_name = os.getcwd() + '/%s.zip' % lambda_name

  if zip_folder():
    print "Attempting to update lambda..."  
    try:
      update = client.update_function_code(
        FunctionName='%s' % lambda_name,
        ZipFile= open(archive_name, 'rb').read(),
#        Publish=True|False,
#        DryRun=True|False
      )
      return True
    except IOError, message:
      print message
      sys.exit(1)

#Add command line args for dry run
def delete():
  lambda_name = json_parser()["initializers"]["name"]

  try:
    delete = client.delete_function(
      FunctionName='%s' % lambda_name
      )
    if check():
      return "Failed to delete Lambda"
    else:
      return True
  except IOError, message:
    print message
    sys.exit(1)

#Add command line args for dry run
def publish():
  lambda_name = json_parser()["initializers"]["name"]
  
  try: 
    publish = client.publish_version(
      FunctionName='%s' % lambda_name,
      )
    return True
  except IOError, message:
    print message
    sys.exit(1)
'''
def is_event_source():

  still working this out
'''

def main():
  if validation():
      if ACTION == "create":
        print "Checking to see if lambda already exists"
        if check():
          print "This function already exists, please use action 'update'"
        else:
          if create():
            if check():
              print "Lambda uploaded successfully"
            else:
              return "False"
              print "Something went wrong.. I checked for your lambda after upload and it isn't there"
          return False
          print "Lambda creation failed.. Check your settings"

      if ACTION == "update":
        if check():
          if update():
            print "Lambda updated"
        else:
          print "No lambda was found.. please create using action 'create'"

      if ACTION == "delete":
        if check():
          if delete():
            print "Lamba deleted successfully"
        else:
          print "No lambda was found.. looks like you have nothing to delete"

      if ACTION == "publish":
        if check():
          if publish():
            print "Lambda v%s successfully published" % json_parser()["initializers"]["version"]
        else:
          print "No lambda was found.. Check your settings"

if __name__ == "__main__":
  main()