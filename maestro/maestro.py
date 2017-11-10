import boto3
import sys
import json
import os
from time import gmtime, strftime
from botocore.exceptions import ClientError

#Clean these up...
import maestro.vpc_location as vpc_location
import maestro.lambda_config as lambda_config

#Get CLI Args
from maestro.cli import ARGS

#Alias module
from maestro.alias import alias_creation as alias_creation
from maestro.alias import alias_destroy as alias_destroy
from maestro.alias import alias_update as alias_update

#Trigger module
from maestro.triggers import create_trigger as create_trigger
from maestro.triggers import remove_invoke_action as delete_trigger

#DLQ module
from maestro.dlq import get_sns_arn
from maestro.dlq import get_sqs_arn

#Everything else
from maestro.security_groups import security_groups as security_groups_method
from maestro.s3_backup import main as s3_backup
from maestro.invoke import main as invoke
from maestro.cloudwatch_sub import cloudwatchSubscription
from maestro.config_validator import validation
from maestro.zip_function import zip_function

DOC = ARGS.filename

client = boto3.client('lambda')
iam = boto3.resource('iam')
roles = boto3.client('iam')

TRACING_TYPES = lambda_config.TRACE_TYPES
ACCEPTED_PROMPT_ACTIONS = lambda_config.ACCEPTED_PROMPT_ACTIONS

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
  print(color.RED + "No json document to read.. Please enter a valid json document" + color.END)

def get_arn():
  role = iam.Role('%s' % json_parser()["initializers"]["role"])
  arn = role.arn
  return arn

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
    subnets = vpc_location.main(json_parser()['vpc_setting']['vpc_name'])
    subnet_ids.extend(subnets)
  else:
    pass

  security_group_id_list = []

  if 'vpc_setting' in json_parser():
    groups = security_groups_method(json_parser()['vpc_setting']['security_group_ids'])
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

  if zip_function(lambda_name):
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

  if zip_function(lambda_name):
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

          if publish_answer.lower() in ACCEPTED_PROMPT_ACTIONS:
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
    subnets = vpc_location.main(json_parser()['vpc_setting']['vpc_name'])
    subnet_ids.extend(subnets)
  else:
    pass

  security_group_id_list = []

  if 'vpc_setting' in json_parser():
    groups = security_groups_method(json_parser()['vpc_setting']['security_group_ids'])
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
  if validation(DOC, current_action=ARGS.action, config_runtime=json_parser()['provisioners']['runtime'], role=json_parser()['initializers']['role'], timeout=json_parser()['provisioners']['timeout']):
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
                if 'alias' in json_parser()['initializers']:
                  if alias_creation(json_parser()['initializers']['name'], json_parser()['initializers']['alias'], ARGS.dry_run, ARGS.publish):
                    print("Alias added successfully")
                    if 'trigger' in json_parser():
                      if create_trigger(json_parser()['initializers']['name'], trigger=True, invoke_method=json_parser()['trigger']['method'], invoke_source=json_parser()['trigger']['source'], alias=json_parser()['initializers']['alias']):
                        if 'logging' in json_parser():
                          name = json_parser()['initializers']['name']
                          role = json_parser()['initializers']['role']
                          region = json_parser()['initializers']['region']
                          dest_lambda = json_parser()['logging']['destination_lambda']
                          dest_alias = json_parser()['logging']['destination_alias']
                          
                          cloudwatchSubscription(name, dest_lambda, dest_alias, region, role)
                        else:
                          pass
                        if 'backup' in json_parser():
                          if s3_backup(json_parser()['initializers']['name'], json_parser()['backup']['bucket_name'], ARGS.dry_run):
                            return 0
                          else:
                            print("Backup failed")
                            return 1
                        else:
                            return 0
                      else:
                        print("Alias failed to created")
                        return 0
                    elif ARGS.create_trigger:
                      if create_trigger(json_parser()['initializers']['name'], trigger=True, invoke_method=json_parser()['trigger']['method'], invoke_source=json_parser()['trigger']['source'], alias=json_parser()['initializers']['alias']):
                        if 'logging' in json_parser():
                          name = json_parser()['initializers']['name']
                          role = json_parser()['initializers']['role']
                          region = json_parser()['initializers']['region']
                          dest_lambda = json_parser()['logging']['destination_lambda']
                          dest_alias = json_parser()['logging']['destination_alias']
                          
                          cloudwatchSubscription(name, dest_lambda, dest_alias, region, role)
                        else:
                          pass
                        if 'backup' in json_parser():
                          if s3_backup(json_parser()['initializers']['name'], json_parser()['backup']['bucket_name'], ARGS.dry_run):
                            return 0
                          else:
                            print("Backup failed")
                            return 1
                        else:
                          return 0
                      else:
                        print("Alias failed to created")
                        return 1
                    elif 'logging' in json_parser():
                      name = json_parser()['initializers']['name']
                      role = json_parser()['initializers']['role']
                      region = json_parser()['initializers']['region']
                      dest_lambda = json_parser()['logging']['destination_lambda']
                      dest_alias = json_parser()['logging']['destination_alias']
                      
                      cloudwatchSubscription(name, dest_lambda, dest_alias, region, role)

                      if 'backup' in json_parser():
                        if s3_backup(json_parser()['initializers']['name'], json_parser()['backup']['bucket_name'], ARGS.dry_run):
                          return 0
                        else:
                          print("Backup failed")
                          return 1
                      else:
                        return 0
                    elif 'backup' in json_parser():
                      if s3_backup(json_parser()['initializers']['name'], json_parser()['backup']['bucket_name'], ARGS.dry_run):
                        return 0
                    else:
                      return 0
                elif ARGS.alias:
                  if alias_creation(json_parser()['initializers']['name'], json_parser()['initializers']['alias'], ARGS.dry_run, ARGS.publish):
                    print("Alias added successfully")
                    if 'trigger' in json_parser():
                      if create_trigger(json_parser()['initializers']['name'], trigger=True, invoke_method=json_parser()['trigger']['method'], invoke_source=json_parser()['trigger']['source'], alias=json_parser()['initializers']['alias']):
                        if 'logging' in json_parser():
                          name = json_parser()['initializers']['name']
                          role = json_parser()['initializers']['role']
                          region = json_parser()['initializers']['region']
                          dest_lambda = json_parser()['logging']['destination_lambda']
                          dest_alias = json_parser()['logging']['destination_alias']
                          
                          cloudwatchSubscription(name, dest_lambda, dest_alias, region, role)
                        else:
                          pass
                        if 'backup' in json_parser():
                          if s3_backup(json_parser()['initializers']['name'], json_parser()['backup']['bucket_name'], ARGS.dry_run):
                            return 0
                          else:
                            print("Backup failed")
                            return 1
                        else:
                          return 0
                      else:
                        print("Alias failed to created")
                        return 1
                    elif ARGS.create_trigger:
                      if create_trigger(json_parser()['initializers']['name'], trigger=True, invoke_method=json_parser()['trigger']['method'], invoke_source=json_parser()['trigger']['source'], alias=json_parser()['initializers']['alias']):
                        if 'logging' in json_parser():
                          name = json_parser()['initializers']['name']
                          role = json_parser()['initializers']['role']
                          region = json_parser()['initializers']['region']
                          dest_lambda = json_parser()['logging']['destination_lambda']
                          dest_alias = json_parser()['logging']['destination_alias']
                          
                          cloudwatchSubscription(name, dest_lambda, dest_alias, region, role)
                        else:
                          pass
                        if 'backup' in json_parser():
                          if s3_backup(json_parser()['initializers']['name'], json_parser()['backup']['bucket_name'], ARGS.dry_run):
                            return 0
                          else:
                            print("Backup failed")
                            return 1
                        else:
                          return 0
                      else:
                        print("Alias failed to created")
                        return 1
                    elif 'backup' in json_parser():
                      if s3_backup(json_parser()['initializers']['name'], json_parser()['backup']['bucket_name'], ARGS.dry_run):
                        return 0
                    else:
                      return 0
                elif 'logging' in json_parser():
                  name = json_parser()['initializers']['name']
                  role = json_parser()['initializers']['role']
                  region = json_parser()['initializers']['region']
                  dest_lambda = json_parser()['logging']['destination_lambda']
                  dest_alias = json_parser()['logging']['destination_alias']
                  
                  cloudwatchSubscription(name, dest_lambda, dest_alias, region, role)

                  if 'backup' in json_parser():
                    if s3_backup(json_parser()['initializers']['name'], json_parser()['backup']['bucket_name'], ARGS.dry_run):
                      return 0
                    else:
                      print("Backup failed")
                      return 1
                  else:
                    return 0
                elif 'backup' in json_parser():
                  if s3_backup(json_parser()['initializers']['name'], json_parser()['backup']['bucket_name'], ARGS.dry_run):
                    return 0
                else:
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
              if s3_backup(json_parser()['initializers']['name'], json_parser()['backup']['bucket_name'], ARGS.dry_run):
                if ARGS.alias:
                  if alias_creation(json_parser()['initializers']['name'], json_parser()['initializers']['alias'], ARGS.dry_run, ARGS.publish):
                    if ARGS.create_trigger:
                      if create_trigger(json_parser()['initializers']['name'], trigger=True, invoke_method=json_parser()['trigger']['method'], invoke_source=json_parser()['trigger']['source'], alias=json_parser()['initializers']['alias']):
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
              if delete_trigger(lambda_name=json_parser()['initializers']['name'], trigger=True, alias=json_parser()['initializers']['alias'], invoke_source=json_parser()['trigger']['source']):
                return 0
              else:
                return 1
            else:
              pass
            
            if 'trigger' in json_parser():
              if create_trigger(json_parser()['initializers']['name'], trigger=True, invoke_method=json_parser()['trigger']['method'], invoke_source=json_parser()['trigger']['source'], alias=json_parser()['initializers']['alias'], event_type=ARGS.event_type, dry_run=ARGS.dry_run):
                return 0
            else:
              if ARGS.create_trigger:
                if create_trigger(json_parser()['initializers']['name'], trigger=True, invoke_method=json_parser()['trigger']['method'], invoke_source=json_parser()['trigger']['source'], alias=json_parser()['initializers']['alias'], event_type=ARGS.event_type, dry_run=ARGS.dry_run):
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
          if alias_creation(json_parser()['initializers']['name'], json_parser()['initializers']['alias'], ARGS.dry_run, ARGS.publish):
            return 0
          else:
            print("Alias creation failed..")
            return 1

      elif ARGS.action == "delete-alias":
        if check():
          if alias_destroy(json_parser()['initializers']['name'], ARGS.alias, ARGS.dry_run):
            return 0
          else:
            return 1

      elif ARGS.action == "update-alias":
        if check():
          if alias_update(json_parser()['initializers']['name'], json_parser()['initializers']['alias'], ARGS.dry_run, ARGS.publish):
            return 0
          else:
            return 1
     
      elif ARGS.action == "invoke":
        if check():
          if invoke(
                json_parser()['initializers']['name'], 
                version=ARGS.version,
                alias=ARGS.alias,
                invoke_type=ARGS.invoke_type,
                payload=ARGS.payload
                ):
            return 0
          else:
            return 1

if __name__ == "__main__":
  main()
