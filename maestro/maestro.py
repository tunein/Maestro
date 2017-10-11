import boto3
import sys
import json
import zipfile
import os
from time import gmtime, strftime
from botocore.exceptions import ClientError

import maestro.vpc_location as vpc_location
import maestro.s3_backup as s3_backup
import maestro.alias as alias 
import maestro.lambda_config as lambda_config
import maestro.security_groups as security_groups_method
import maestro.invoke as invoke
from maestro.cli import ARGS
from maestro.triggers import creation as create_trigger
from maestro.triggers import remove_invoke_action as delete_trigger
from maestro.dlq import get_sns_arn
from maestro.dlq import get_sqs_arn

DOC = ARGS.filename

client = boto3.client('lambda')
iam = boto3.resource('iam')
roles = boto3.client('iam')

AVAIL_RUNTIMES = lambda_config.AVAIL_RUNTIMES
AVAIL_ACTIONS = lambda_config.AVAIL_ACTIONS
TRACING_TYPES = lambda_config.TRACE_TYPES

yes_or_no = ['y', 'n']

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

def file_type():
  print(color.CYAN + "validating file type..." + color.END)
  if len(DOC)>0:
    if DOC.lower().endswith('.json'):
      return True
    return False
  print(color.RED + "Please enter a valid json document after your action" + color.END)

def json_parser():
  with open('%s' % DOC) as json_data:
    read = json.load(json_data)
    return read
    return True
  print(color.RED + "No json document to read.. Please enter a valid json document" + color.END)

def validate_action():
  if len(json_parser()["initializers"]["name"])>0:
    if any(action in ARGS.action for action in AVAIL_ACTIONS):
      return True
    print(color.RED + "Not a valid action" + color.END)
  print(color.RED + "Check your json document for the right syntax.." + color.END)

def validate_runtime():
  if len(json_parser()["initializers"]["name"])>0:
    RUNTIME = json_parser()["provisioners"]["runtime"]
    print(color.CYAN + "validating runtime %s..." % RUNTIME + color.END)
    if any(runtime in RUNTIME for runtime in AVAIL_RUNTIMES):
      return True
    print(color.RED + "Not a valid runtime" + color.END)

def validate_role():
  name = json_parser()["initializers"]["role"]
  print(color.CYAN + "validating role %s..." % name + color.END)
  data = iam.role_name=name
  if len(data)>0:
    return True
  print(color.RED + "invalid role" + color.END)  

def validate_timeout():
  timeout = json_parser()["provisioners"]["timeout"]
  acceptable_range = range(1,301)
  if timeout in acceptable_range:
    return True
  print(color.RED + "Timeout should between between 1 and 300 seconds, please adjust" + color.END)

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
  folder_path = os.curdir + '/dist'
  grab_lambda = os.walk(folder_path)
  length = len(folder_path)

  try:
    zipped_lambda = zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED)
    for root, folders, files in grab_lambda:
      for folder_name in folders:
        absolute_path = os.path.join(root, folder_name)
        shortened_path = os.path.join(root[length:], folder_name)
        print(color.CYAN + "Adding '%s' to package." % shortened_path + color.END)
        zipped_lambda.write(absolute_path, shortened_path)
      for file_name in files:
        absolute_path = os.path.join(root, file_name)
        shortened_path = os.path.join(root[length:], file_name)
        print(color.CYAN + "Adding '%s' to package." % shortened_path + color.END)
        zipped_lambda.write(absolute_path, shortened_path)
    print(color.CYAN + "'%s' lambda packaged successfully." % lambda_name + color.END)
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

def create():
  lambda_name = json_parser()["initializers"]["name"]
  archive_name = os.getcwd() + '/%s.zip' % lambda_name

  subnet_ids = []

  if 'vpc_setting' in json_parser():
    subnets = vpc_location.main()
    subnet_ids.extend(subnets)
  else:
    pass

  security_group_id_list = []

  if 'vpc_setting' in json_parser():
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

  if ARGS.publish:
    pub = True
  else:
    pub = False

  if 'variables' in json_parser():
    env_vars = json_parser()['variables']
  else:
    env_vars = { }

  target_arn = { }

  if 'dead_letter_config' in json_parser():
    dlq_type = json_parser()['dead_letter_config']['type']
    name = json_parser()['dead_letter_config']['target_name']
    if dlq_type == 'sns':
      arn = get_sns_arn(name)
      target_arn.update({'TargetArn': arn})
    elif dlq_type == 'sqs':
      arn = get_sqs_arn(name)
      target_arn.update({'TargetArn': arn})
    else:
      raise RuntimeError('No valid DLQ type found')
  else:
    pass

  trace_type = { }

  if 'tracing_mode' in json_parser()['initializers']:
    mode = json_parser()['initializers']['tracing_mode']
    if mode in TRACING_TYPES:
      if mode == "active":
        capmode = "Active"
        trace_type.update({'Mode': capmode})
      elif mode == "passthrough":
        capmode = "PassThrough"
        trace_type.update({'Mode': capmode})
    else:
      raise RuntimeError('No valid trace mode found')
  else:
    trace_type = {'Mode': 'PassThrough'}

  if zip_folder():
    if ARGS.dry_run:
      print(color.BOLD + "***Dry Run option enabled***" + color.END)
      print(color.PURPLE + "Would have attempted to create the following:" + color.END)
      print(color.PURPLE + "FunctionName: %s" % lambda_name + color.END)
      print(color.PURPLE + "Runtime: %s" % json_parser()["provisioners"]["runtime"] + color.END)
      print(color.PURPLE + "Role: %s" % get_arn() + color.END)
      print(color.PURPLE + "Handler: %s" % json_parser()["initializers"]["handler"] + color.END)
      print(color.PURPLE + "Archive: %s" % archive_name + color.END)
      print(color.PURPLE + "Description: %s" % json_parser()["initializers"]["description"] + color.END)
      print(color.PURPLE + "Timeout: %s" % json_parser()["provisioners"]["timeout"] + color.END)
      print(color.PURPLE + "Memory Size: %s" % json_parser()["provisioners"]["mem_size"] + color.END)
      print(color.PURPLE + "VPC Config: %s" % vpc_config + color.END)
      print(color.PURPLE + "Environment Variables: %s" % env_vars + color.END)
      print(color.PURPLE + "DLQ Target: %s" % target_arn)
      print(color.PURPLE + "Tracing Config: %s" % trace_type)
      print(color.PURPLE + "Tags: %s" % tags)
      return True
    else:
      print(color.CYAN + "Attempting to create lambda..." + color.END)
      try:
        create = client.create_function(
          FunctionName='%s' % lambda_name,
          Runtime='%s' % json_parser()["provisioners"]["runtime"],
          Role='%s' % get_arn(),
          Handler='%s' % json_parser()["initializers"]["handler"],
          Code={
            'ZipFile': open(archive_name, 'rb').read()
          },
          Description='%s' % json_parser()["initializers"]["description"],
          Timeout=json_parser()["provisioners"]["timeout"],
          MemorySize=json_parser()["provisioners"]["mem_size"],
          Publish=pub,
          VpcConfig=vpc_config,
          Environment={
            'Variables': env_vars
            },
          DeadLetterConfig=target_arn,
          TracingConfig=trace_type,
          Tags=tags
        )
        if create['ResponseMetadata']['HTTPStatusCode'] == 201:
          return True
        else:
          return False
      except ClientError as error:
        print(color.RED + error.response['Error']['Message'] + color.END)
        sys.exit(1)

def update():
  lambda_name = json_parser()["initializers"]["name"]
  archive_name = os.getcwd() + '/%s.zip' % lambda_name  

  if zip_folder():
    print(color.CYAN + "Attempting to update lambda..." + color.END)

    if ARGS.dry_run:
      print(color.PURPLE + "***Dry Run option enabled, running dry run code-update***" + color.END)
      run = True
    else:
      run = False

    if ARGS.publish:
      if ARGS.dry_run:
        answer = False
      else:
        answer = True
    else:
      if ARGS.dry_run:
        answer = False
      else:
        if ARGS.no_pub:
          answer = False
        else:
          publish_answer = input("Would you like to publish this update? ('y/n'): ")

          if publish_answer.lower() in yes_or_no:
            if publish_answer == 'y':
              answer = True
              print(color.CYAN + "Publishing update" + color.END)
            if publish_answer == 'n':
              answer = False
              print(color.CYAN + "Updating lambda without publishing" + color.END)
          else:
            print(color.RED + "Please respond with 'y' for yes or 'n' for no!" + color.END)

    try:
      update = client.update_function_code(
        FunctionName='%s' % lambda_name,
        ZipFile= open(archive_name, 'rb').read(),
        Publish=answer,
        DryRun=run
      )
      if update['ResponseMetadata']['HTTPStatusCode'] == 200:
        if ARGS.dry_run:
          print(color.PURPLE + "***Dry Run Successful!***" + color.END)
          return True
        else:
          print(color.CYAN + "Lambda updated!" + color.END)
          return True
      else:
        return False
    except ClientError as error:
      print(color.RED + error.response['Error']['Message'] + color.END)
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
    print(color.RED + error.response['Error']['Message'] + color.END)

def update_config():
  lambda_name = json_parser()["initializers"]["name"]

  subnet_ids = []

  if 'vpc_setting' in json_parser():
    subnets = vpc_location.main()
    subnet_ids.extend(subnets)
  else:
    pass

  security_group_id_list = []

  if 'vpc_setting' in json_parser():
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
      print(color.RED + error.response['Error']['Message'] + color.END)
  else:
    pass

  if len(subnet_ids)>0:
    vpc_config = {
                  'SubnetIds': subnet_ids,
                  'SecurityGroupIds': security_group_id_list
                }
  else:
    vpc_config = { }

  if 'variables' in json_parser():
    env_vars = json_parser()['variables']
  else:
    env_vars = { }

  target_arn = { }

  if 'dead_letter_config' in json_parser():
    dlq_type = json_parser()['dead_letter_config']['type']
    name = json_parser()['dead_letter_config']['target_name']
    if dlq_type == 'sns':
      arn = get_sns_arn(name)
      target_arn.update({'TargetArn': arn})
    elif dlq_type == 'sqs':
      arn = get_sqs_arn(name)
      target_arn.update({'TargetArn': arn})
    else:
      raise RuntimeError('No valid DLQ type found')
  else:
    print('No DLQ resource found, passing')
    pass

  trace_type = { }

  if 'tracing_mode' in json_parser()['initializers']:
    mode = json_parser()['initializers']['tracing_mode']
    if mode in TRACING_TYPES:
      if mode == "active":
        capmode = "Active"
        trace_type.update({'Mode': capmode})
      elif mode == "passthrough":
        capmode = "PassThrough"
        trace_type.update({'Mode': capmode})
    else:
      raise RuntimeError('No valid trace mode found')
  else:
    trace_type = {'Mode': 'PassThrough'}

  try:
    update_configuration = client.update_function_configuration(
      FunctionName='%s' % lambda_name,
      Role='%s' % get_arn(),
      Handler='%s' % json_parser()["initializers"]["handler"],
      Description='%s' % json_parser()["initializers"]["description"],
      Timeout=json_parser()["provisioners"]["timeout"],
      MemorySize=json_parser()["provisioners"]["mem_size"],
      VpcConfig=vpc_config,
      Runtime='%s' % json_parser()["provisioners"]["runtime"],
      Environment={
          'Variables': env_vars
        },
      DeadLetterConfig=target_arn,
      TracingConfig=trace_type
      )
    if update_configuration['ResponseMetadata']['HTTPStatusCode'] == 200:
      return True
    else:
      return False
  except ClientError as error:
    print(color.RED + error.response['Error']['Message'] + color.END)

def delete():
  lambda_name = json_parser()["initializers"]["name"]

  if ARGS.dry_run:
    try:
      print(color.PURPLE + "***Dry run option enabled, dry running a deletion***" + color.END)
      alias = client.list_aliases(
                      FunctionName='%s' % lambda_name,
                      )

      dump_json = json.dumps(alias, indent=4) 
      load = json.loads(dump_json)

      aliases = []

      for names in load['Aliases']:    
        aliases.append(names['Name'])

      print(color.PURPLE + "Would delete:" + color.END)
      print(color.PURPLE + "Lambda: %s" % lambda_name + color.END)
      for item in aliases:
        print(color.PURPLE + "Alias: %s" % item + color.END)

      versions = client.list_versions_by_function(
                  FunctionName='%s' % lambda_name,
                )

      version_json = json.dumps(versions, indent=4)
      load_json = json.loads(version_json)
      versions = load_json['Versions']
      avail_versions = []

      for version in versions:
        avail_versions.append(version['Version'])

      for vers in avail_versions:
        print(color.PURPLE + "Version: %s" % vers + color.END)
    except ClientError as error:
      print(color.RED + error.response['Error']['Message'] + color.END)
  else:
    double_check = input("Are you SURE you want to delete this lambda (y/n)? ")
    lowered_checked = double_check.lower()

    if lowered_checked == 'y':
      try:
        delete = client.delete_function(
          FunctionName='%s' % lambda_name
          )
        if check():
          print(color.RED + "Failed to delete Lambda" + color.END)
          return False
        else:
          print(color.CYAN + "Lambda %s deleted successfully" % lambda_name + color.END)
          return True
      except ClientError as error:
        print(color.RED + error.response['Error']['Message'] + color.END)
        sys.exit(1)
    else:
      print(color.RED + "Exiting" + color.END)
      sys.exit(1)

def publish():
  lambda_name = json_parser()["initializers"]["name"]
  
  try:
    if ARGS.version_description:
      version_descript = ARGS.version_description
      print("Descript: %s" % version_descript)
    else:
      version_descript = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
      print("Descript: %s" % version_descript)

    publish = client.publish_version(
      FunctionName='%s' % lambda_name,
      Description=version_descript
      )
    if publish['ResponseMetadata']['HTTPStatusCode'] == 201:
      print(color.CYAN + "Successfully published %s version %s" % (lambda_name, publish['Version']) + color.END)
      return 0
    else:
      return False    
  except ClientError as error:
    print(color.RED + error.response['Error']['Message'] + color.END)
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
            if ARGS.dry_run:
              return 0
            else:
              if check():
                print("Lambda uploaded successfully")
                if 'backup' in json_parser():
                  if s3_backup.main():
                    if 'alias' in json_parser()['initializers']:
                      if alias.alias_creation():
                        print("Alias added successfully")
                        if 'trigger' in json_parser():
                          if create_trigger():
                            return 0
                        elif ARGS.create_trigger:
                          if create_trigger():
                            return 0
                          else:
                            print("Alias failed to created")
                            return 1
                        else:
                          return 0
                    elif ARGS.alias:
                      if alias.alias_creation():
                        print("Alias added successfully")
                        if 'trigger' in json_parser():
                          if create_trigger():
                            return 0
                        elif ARGS.create_trigger:
                          if create_trigger():
                            return 0
                          else:
                            print("Alias failed to created")
                            return 1
                        else:
                          return 0
                    else:
                      return 0
                  else:
                    print("Backup failed..")
                    return 1
                else:
                  print("Backup option not selected, skipping...")
                  return 0
              else:
                print("Something went wrong.. I checked for your lambda after upload and it isn't there")
                return 1
          else:
            print("Lambda creation failed.. Check your settings")             
            return 1

      elif ARGS.action == 'update-code':
        if check():
          if update():
            if 'backup' in json_parser():
              if s3_backup.main():
                if ARGS.alias:
                  if alias.alias_creation():
                    if ARGS.create_trigger:
                      if create_trigger():
                        return 0
                      else:
                        return 1
                  else:
                    print("Alias failed to created")
                    return 1
              else:
                print("Backup failed..")
                return 1
            else:
              print("Backup option not selected, skipping...")
              return 0
        else:
          print("No lambda was found.. please create using action 'create'")

      elif ARGS.action == "update-config":
        if check():
          if update_config():

            if ARGS.delete_trigger:
              if delete_trigger():
                return 0
              else:
                return 1
            else:
              pass
            
            if 'trigger' in json_parser():
              if create_trigger():
                return 0
            else:
              if ARGS.create_trigger:
                if create_trigger():
                  return 0
                else:
                  return 1
              else:
                pass

            print("Lambda configuration updated!")
            return 0
          else:
            print("Lambda configuration not updated, please check your settings")
            return 1
        print("Check failed, please check settings")
        return 1

      elif ARGS.action == "delete":
        if check():
          if delete():
            return 0
        else:
          print("No lambda was found.. looks like you have nothing to delete")

      elif ARGS.action == "publish":
        if check():
          if publish():
            return 0
        else:
          print("No lambda was found.. Check your settings")

      elif ARGS.action == "create-alias":
        if check():
          if alias.alias_creation():
            return 0
          else:
            print("Alias creation failed..")
            return 1

      elif ARGS.action == "delete-alias":
        if check():
          if alias.alias_destroy():
            return 0
          else:
            return 1

      elif ARGS.action == "update-alias":
        if check():
          if alias.alias_update():
            return 0
          else:
            return 1
     
      elif ARGS.action == "invoke":
        if check():
          if invoke.test_invoke():
            return 0
          else:
            return 1

if __name__ == "__main__":
  main()
