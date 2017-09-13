import boto3
import sys
import json
import zipfile
import os
from botocore.exceptions import ClientError

import maestro.vpc_location as vpc_location
import maestro.s3_backup as s3_backup
import maestro.alias as alias 
import maestro.lambda_config as lambda_config
import maestro.security_groups as security_groups_method
from maestro.cli import ARGS
from maestro.triggers import creation as create_trigger
from maestro.triggers import remove_invoke_action as delete_trigger

#USER_ACTION = args
DOC = ARGS.filename
#ACTION = USER_ACTION.lower()

client = boto3.client('lambda')
iam = boto3.resource('iam')
roles = boto3.client('iam')

AVAIL_RUNTIMES = lambda_config.AVAIL_RUNTIMES
AVAIL_ACTIONS = lambda_config.AVAIL_ACTIONS

yes_or_no = ['y', 'n']

def file_type():
  print("validating file type...")
  if len(DOC)>0:
    if DOC.lower().endswith('.json'):
      return True
    return False
  print("Please enter a valid json document after your action")

def json_parser():
  with open('%s' % DOC) as json_data:
    read = json.load(json_data)
    return read
    return True
  print("No json document to read.. Please enter a valid json document")

def validate_action():
  if len(json_parser()["initializers"]["name"])>0:
    if any(action in ARGS.action for action in AVAIL_ACTIONS):
      return True
    print("Not a valid action")
  print("Check your json document for the right syntax..")

def validate_runtime():
  if len(json_parser()["initializers"]["name"])>0:
    RUNTIME = json_parser()["provisioners"]["runtime"]
    print("validating runtime %s..." % RUNTIME)
    if any(runtime in RUNTIME for runtime in AVAIL_RUNTIMES):
      return True
    print("Not a valid runtime")

def validate_role():
  name = json_parser()["initializers"]["role"]
  print("validating role %s..." % name)
  data = iam.role_name=name
  if len(data)>0:
    return True
  print("invalid role")  

def validate_timeout():
  timeout = json_parser()["provisioners"]["timeout"]
  acceptable_range = range(1,301)
  if timeout in acceptable_range:
    return True
  print("Timeout should between between 1 and 300 seconds, please adjust")

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
        print("Adding '%s' to package." % shortened_path)
        zipped_lambda.write(absolute_path, shortened_path)
      for file_name in files:
        absolute_path = os.path.join(root, file_name)
        shortened_path = os.path.join(root[length:], file_name)
        print("Adding '%s' to package." % shortened_path)
        zipped_lambda.write(absolute_path, shortened_path)
    print("'%s' lambda packaged successfully." % lambda_name)
    return True
  except IOError:
    print(message)
    sys.exit(1)
  except OSError:
    print(message)
    sys.exit(1)
  except zipfile.BadZipfile:
    print(message)
    sys.exit(1)
  finally:
    zipped_lambda.close()

def check():
  proposed_function = json_parser()["initializers"]["name"]
  existing_functions = client.list_functions()
  parse = json.dumps(existing_functions)
  load = json.loads(parse) 
  functions = load["Functions"]

  current_functions = []

  for function in functions:
    names = function['FunctionName']
    append = current_functions.append(names)

  if proposed_function in current_functions:
    return True
  else:
    return False

#Add command line args for dry run
def create():
  lambda_name = json_parser()["initializers"]["name"]
  archive_name = os.getcwd() + '/%s.zip' % lambda_name

  subnet_ids = []

  if 'vpc_name' in json_parser()['vpcconfig']:
    subnets = vpc_location.main()
    subnet_ids.extend(subnets)
  else:
    pass

  security_group_id_list = []

  if 'security_group_ids' in json_parser()['vpcconfig']:
    groups = security_groups_method.main()
    security_group_id_list.extend(groups)
  else:
    pass

  tags = {}

  if 'tags' in json_parser():
    tags.update(json_parser()['tags'])
  else:
    pass

  if len(subnet_ids)>0:
    vpc_config = {
                    'SubnetIds': subnet_ids,
                    'SecurityGroupIds': security_group_id_list
                  }
  else:
    vpc_config = { }

  if zip_folder():
    print("Attempting to create lambda...")
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
        MemorySize=json_parser()["provisioners"]["mem_size"],
        VpcConfig=vpc_config,
        Tags=tags
      )
      if create['ResponseMetadata']['HTTPStatusCode'] == 201:
        return True
      else:
        return False
    except ClientError as error:
      print(error.response['Error']['Message'])
      sys.exit(1)

#Add command line args for dry run
def update():
  lambda_name = json_parser()["initializers"]["name"]
  archive_name = os.getcwd() + '/%s.zip' % lambda_name  

  if zip_folder():
    print("Attempting to update lambda...")

    if ARGS.publish:
      answer = True
    else:
      publish_answer = input("Would you like to publish this update? ('y/n'): ")

      if publish_answer.lower() in yes_or_no:
        if publish_answer == 'y':
          answer = True
          print("Publishing update")
        if publish_answer == 'n':
          answer = False
          print("Updating lambda without publishing")
      else:
        print("Please respond with 'y' for yes or 'n' for no!")

    try:
      update = client.update_function_code(
        FunctionName='%s' % lambda_name,
        ZipFile= open(archive_name, 'rb').read(),
        Publish=answer
        #DryRun=True|False
      )
      if update['ResponseMetadata']['HTTPStatusCode'] == 200:
        return True
      else:
        return False
    except ClientError as error:
      print(error.response['Error']['Message'])
      sys.exit(1)

def list_lambdas():
  lambda_name = json_parser()["initializers"]["name"]
  try:
    response = client.list_functions(
                FunctionVersion='ALL'
              )
    dump = json.dumps(response, indent=4)
    load = json.loads(dump)
    
    for function in load['Functions']:
      if lambda_name in function['FunctionName']:
        splitter = function['FunctionArn'].split(':')[0:7]
        joiner = ':'.join(map(str, splitter))
        return joiner
  except ClientError as error:
    print(error.response['Error']['Message'])

def update_config():
  lambda_name = json_parser()["initializers"]["name"]

  subnet_ids = []

  if 'vpc_name' in json_parser()['vpcconfig']:
    subnets = vpc_location.main()
    subnet_ids.extend(subnets)
  else:
    pass

  security_group_id_list = []

  if 'security_group_ids' in json_parser()['vpcconfig']:
    groups = security_groups_method.main()
    security_group_id_list.extend(groups)
  else:
    pass

  tags = {}

  if 'tags' in json_parser():
    tags.update(json_parser()['tags'])
    try:
      generate_tags = client.tag_resource(
                        Resource=list_lambdas(),
                        Tags=tags
                      )
    except ClientError as error:
      print(error.response['Error']['Message'])
  else:
    pass

  if len(subnet_ids)>0:
    vpc_config = {
                  'SubnetIds': subnet_ids,
                  'SecurityGroupIds': security_group_id_list
                }
  else:
    vpc_config = { }

  try:
    update_configuration = client.update_function_configuration(
      FunctionName='%s' % lambda_name,
      Role='%s' % get_arn(),
      Handler='%s' % json_parser()["initializers"]["name"],
      Description='%s' % json_parser()["initializers"]["description"],
      Timeout=json_parser()["provisioners"]["timeout"],
      MemorySize=json_parser()["provisioners"]["mem_size"],
      VpcConfig=vpc_config,
      Runtime='%s' % json_parser()["provisioners"]["runtime"],
      )
    if update_configuration['ResponseMetadata']['HTTPStatusCode'] == 200:
      return True
    else:
      return False
  except ClientError as error:
    print(error.response['Error']['Message'])

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
  except ClientError as error:
    print(error.response['Error']['Message'])
    sys.exit(1)

#Add command line args for dry run
def publish():
  lambda_name = json_parser()["initializers"]["name"]
  
  try: 
    publish = client.publish_version(
      FunctionName='%s' % lambda_name,
      )
    if publish['ResponseMetadata']['HTTPStatusCode'] == 201:
      print("Successfully published %s version %s" % (lambda_name, publish['Version']))
      return True 
    else:
      return False    
  except ClientError as error:
    print(error.response['Error']['Message'])
    sys.exit(1)

'''
def is_event_source():

  still working this out
'''

def main():
  if validation():
      if ARGS.action == 'create':
        print("Checking to see if lambda already exists")
        if check():
          print("This function already exists, please use action 'update'")
        else:
          if create():
            if check():
              print("Lambda uploaded successfully")
              if 'backup' in json_parser():
                print("Backup option selected.. backing up to s3!")
                if s3_backup.main():
                  if ARGS.alias:
                    if alias.alias_creation():
                      print("Alias added successfully")
                      if ARGS.create_trigger:
                        if create_trigger():
                          return True
                        else:
                          return False
                    else:
                      print("Alias failed to created")
                      return False
                else:
                  print("Backup failed..")
                  return False
              else:
                print("Backup option not selected, skipping...")
                return False
            else:
              return "False"
              print("Something went wrong.. I checked for your lambda after upload and it isn't there")
          return False
          print("Lambda creation failed.. Check your settings")

      if ARGS.action == 'update-code':
        if check():
          if update():
            print("Lambda updated")
            if 'backup' in json_parser():
              print("Backup option selected.. backing up to s3!")
              if s3_backup.main():
                if ARGS.alias:
                  if alias.alias_creation():
                    print("Alias added successfully")
                    if ARGS.create_trigger:
                      if create_trigger():
                        return True
                      else:
                        return False
                  else:
                    print("Alias failed to created")
                    return False
              else:
                print("Backup failed..")
                return False
            else:
              print("Backup option not selected, skipping...")
              return False
        else:
          print("No lambda was found.. please create using action 'create'")

      if ARGS.action == "update-config":
        if check():
          if update_config():
            print("Lambda configuration updated!")
            return True
          else:
            print("Lambda configuration not updated, please check your settings")
            return False
        print("Check failed, please check settings")
        return False

      if ARGS.action == "delete":
        if check():
          if delete():
            print("Lambda deleted successfully")
            return True
        else:
          print("No lambda was found.. looks like you have nothing to delete")

      if ARGS.action == "publish":
        if check():
          if publish():
            return True
        else:
          print("No lambda was found.. Check your settings")

      if ARGS.action == "create-alias":
        if check():
          if alias.alias_creation():
            print("Alias added successfully")
            return True
          else:
            print("Alias creation failed..")
            return False

      if ARGS.action == "delete-alias":
        if check():
          if alias.alias_destroy():
            return True
          else:
            return False

      if ARGS.action == "update-alias":
        if check():
          if alias.alias_update():
            return True
          else:
            return False

if __name__ == "__main__":
  main()
