#External libs
import sys
import json
import os

#Our modules
from maestro.main import main

'''
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

#Core actions
from maestro.create_lambda import create
from maestro.publish_lambda import publish
from maestro.delete_lambda import delete
from maestro.update_lambda_code import update_code
from maestro.update_lambda_config import update_config

#Everything else
from maestro.security_groups import security_groups as security_groups_method
from maestro.s3_backup import main as s3_backup
from maestro.invoke import main as invoke
from maestro.cloudwatch_sub import cloudwatchSubscription
from maestro.config_validator import validation
from maestro.zip_function import zip_function
from maestro.check_existence import check
from maestro.role_arn import get_arn
import maestro.vpc_location as vpc_location
import maestro.lambda_config as lambda_config
'''

DOC = ARGS.filename

client = boto3.client('lambda')

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

def main():
  if validation(DOC, current_action=ARGS.action, config_runtime=json_parser()['provisioners']['runtime'], role=json_parser()['initializers']['role'], timeout=json_parser()['provisioners']['timeout']):
      if ARGS.action == 'create':
        
        lambda_name = json_parser()['initializers']['name']
        alias = json_parser()['initializers']['alias']
        runtime = json_parser()['provisioners']['runtime']
        role = json_parser()['initializers']['role']
        handler = json_parser()['initializers']['handler']
        description = json_parser()['initializers']['description']
        timeout = json_parser()['provisioners']['timeout']
        mem_size = json_parser()['provisioners']['mem_size']
        vpc_setting = True
        config_vpc_name = json_parser()['vpc_setting']['vpc_name']
        config_security_groups = json_parser()['vpc_setting']['security_group_ids']

        print("Checking to see if lambda already exists")
        if check(json_parser()['initializers']['name']):
          print("This function already exists, please use action 'update'")
        else:
          if create(lambda_name, runtime, role, handler, description, timeout, mem_size, vpc_setting, config_vpc_name, config_security_groups):
            if ARGS.dry_run:
              return 0
            else:
              if check(json_parser()['initializers']['name']):
                print("Lambda uploaded successfully")
                if 'alias' in json_parser()['initializers']:
                  if alias_creation(json_parser()['initializers']['name'], json_parser()['initializers']['alias'], ARGS.dry_run, ARGS.publish):
                    print("Alias added successfully")
                    if 'trigger' in json_parser():
                      if create_trigger(json_parser()['initializers']['name'], trigger=True, invoke_method=json_parser()['trigger']['method'], invoke_source=json_parser()['trigger']['source'], alias=json_parser()['initializers']['alias'], event_type=ARGS.event_type, dry_run=ARGS.dry_run):
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
                      if create_trigger(json_parser()['initializers']['name'], trigger=True, invoke_method=json_parser()['trigger']['method'], invoke_source=json_parser()['trigger']['source'], alias=json_parser()['initializers']['alias'], event_type=ARGS.event_type, dry_run=ARGS.dry_run):
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
                      if create_trigger(json_parser()['initializers']['name'], trigger=True, invoke_method=json_parser()['trigger']['method'], invoke_source=json_parser()['trigger']['source'], alias=json_parser()['initializers']['alias'], event_type=ARGS.event_type, dry_run=ARGS.dry_run):
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
                      if create_trigger(json_parser()['initializers']['name'], trigger=True, invoke_method=json_parser()['trigger']['method'], invoke_source=json_parser()['trigger']['source'], alias=json_parser()['initializers']['alias'], event_type=ARGS.event_type, dry_run=ARGS.dry_run):
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
        if check(json_parser()['initializers']['name']):
          if update_code(json_parser()['initializers']['name'], dry_run=ARGS.dry_run, publish=ARGS.publish, no_pub=ARGS.no_pub):
            if 'backup' in json_parser():
              if s3_backup(json_parser()['initializers']['name'], json_parser()['backup']['bucket_name'], ARGS.dry_run):
                if ARGS.alias:
                  if alias_creation(json_parser()['initializers']['name'], json_parser()['initializers']['alias'], ARGS.dry_run, ARGS.publish):
                    if ARGS.create_trigger:
                      if create_trigger(json_parser()['initializers']['name'], trigger=True, invoke_method=json_parser()['trigger']['method'], invoke_source=json_parser()['trigger']['source'], alias=json_parser()['initializers']['alias'], event_type=ARGS.event_type, dry_run=ARGS.dry_run):
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
        if check(json_parser()['initializers']['name']):

          lambda_name = json_parser()['initializers']['name']
          runtime = json_parser()['provisioners']['runtime']
          role = json_parser()['initializers']['role']
          handler = json_parser()['initializers']['handler']
          description = json_parser()['initializers']['description']
          timeout = json_parser()['provisioners']['timeout']
          mem_size = json_parser()['provisioners']['mem_size']
          vpc_setting = True
          config_vpc_name = json_parser()['vpc_setting']['vpc_name']
          config_security_groups = json_parser()['vpc_setting']['security_group_ids']
          tags = json_parser()['tags']

          if update_config(lambda_name=lambda_name, handler=handler, description=description, timeout=timeout, mem_size=mem_size, role=role, runtime=runtime, vpc_setting=vpc_setting, config_vpc_name=config_vpc_name, config_security_groups=config_security_groups, new_tags=tags):
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
        if check(json_parser()['initializers']['name']):
          if delete(json_parser()['initializers']['name']):
            return 0
        else:
          print("No lambda was found.. looks like you have nothing to delete")

      elif ARGS.action == "publish":
        if check(json_parser()['initializers']['name']):
          if publish(json_parser()['initializers']['name']):
            return 0
        else:
          print("No lambda was found.. Check your settings")

      elif ARGS.action == "create-alias":
        if check(json_parser()['initializers']['name']):
          if alias_creation(json_parser()['initializers']['name'], json_parser()['initializers']['alias'], ARGS.dry_run, ARGS.publish):
            return 0
          else:
            print("Alias creation failed..")
            return 1

      elif ARGS.action == "delete-alias":
        if check(json_parser()['initializers']['name']):
          if alias_destroy(json_parser()['initializers']['name'], ARGS.alias, ARGS.dry_run):
            return 0
          else:
            return 1

      elif ARGS.action == "update-alias":
        if check(json_parser()['initializers']['name']):
          if alias_update(json_parser()['initializers']['name'], json_parser()['initializers']['alias'], ARGS.dry_run, ARGS.publish):
            return 0
          else:
            return 1
     
      elif ARGS.action == "invoke":
        if check(json_parser()['initializers']['name']):
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
