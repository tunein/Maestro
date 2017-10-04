import boto3
import maestro.lambda_config as lambda_config
import sys
import json
import zipfile
import os
from botocore.exceptions import ClientError
from maestro.cli import ARGS

client = boto3.client('lambda')
iam = boto3.resource('iam')
roles = boto3.client('iam')
DOC = ARGS.filename

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
  print("No json document to read.. Please enter a valid json document")

def alias_creation():
  lambda_name = json_parser()["initializers"]["name"]

  alias = client.list_aliases(
    FunctionName='%s' % lambda_name,
    )

  dump_json = json.dumps(alias, indent=4) 
  load = json.loads(dump_json)

  aliases = []

  for names in load['Aliases']:    
    aliases.append(names['Name'])

  if 'alias' in json_parser()['initializers']:
    if json_parser()['initializers']['alias'] in aliases:
      if ARGS.publish:
        if alias_update():
          return True
      else:
        ask = input("Alias exists, would you like to update it (y/n)? ")
        if ask == 'y':
          if alias_update():
            print("Attempting to update alias %s" % ARGS.alias)
            return True
          else:
            return False
        else:
          print("Exiting!")
          sys.exit(1)  
    else:
      if ARGS.dry_run:
        alias_name = ARGS.alias
        print(color.PURPLE + "***Dry run option enabled***" + color.END)
        print(color.PURPLE + "Would have created alias: %s for %s" % (ARGS.alias, lambda_name) + color.END)
      else:
        alias_name = json_parser()['initializers']['alias']
        pass
  
  elif ARGS.alias:
    if ARGS.alias in aliases:
      if ARGS.publish:
        if alias_update():
          return True
      else:
        ask = input("Alias exists, would you like to update it (y/n)? ")
        if ask == 'y':
          if alias_update():
            print("Attempting to update alias %s" % ARGS.alias)
            return True
          else:
            return False
        else:
          print("Exiting!")
          sys.exit(1)
    else:
      if ARGS.dry_run:
        alias_name = ARGS.alias
        print(color.PURPLE + "***Dry run option enabled***" + color.END)
        print(color.PURPLE + "Would have created alias: %s for %s" % (ARGS.alias, lambda_name) + color.END)
      else:
        alias_name = ARGS.alias
        pass
  else:
    get_alias_name = input("What would you like this alias to be called? ")
    alias_name = get_alias_name.lower()
    if alias_name in aliases:
      ask = input("Alias exists, would you like to update it (y/n)? ")
      if ask == 'y':
        if alias_update():
          print("Attempting to update alias %s" % ARGS.alias)
          return True
        else:
          return False
      else:
        print("Exiting!")
        sys.exit(1)


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

  if ARGS.publish:
    function_version = max(avail_versions)
  else:
    function_version = input("What version would you like to create an alias for? ")
  
  if ARGS.dry_run:
    print(color.PURPLE + "Dry run creating alias '%s' for version '%s' on lambda '%s'" % (alias_name, function_version, lambda_name) + color.END)
    return True
  else:
    pass

  if function_version in avail_versions: 
    try:
      add_alias = client.create_alias(
        FunctionName='%s' % lambda_name,
        Name='%s' % alias_name,
        FunctionVersion='%s' % function_version,
      )
      if add_alias['ResponseMetadata']['HTTPStatusCode'] == 201:
        print("Adding alias '%s' to lambda '%s' version '%s'" % (alias_name, lambda_name, function_version))
        return True
      else:
        return False
    except ClientError as error:
      print(error.response['Error']['Message'])
  else:
    print("I can't find that version, check list and find again")

def alias_destroy():
  lambda_name = json_parser()["initializers"]["name"]

  alias = client.list_aliases(
    FunctionName='%s' % lambda_name,
    )

  dump_json = json.dumps(alias, indent=4) 
  load = json.loads(dump_json)

  aliases = []

  for names in load['Aliases']:
    print("Function Version: '%s', Alias: '%s'" % (names['FunctionVersion'], names['Name']))
    aliases.append(names['Name'])

  if len(aliases) != 0:
    if ARGS.alias:
      alias_name = ARGS.alias
    else:
      alias_name = input("What alias would you like to delete? ")

    if alias_name in aliases:
      if ARGS.dry_run:
        print(color.PURPLE + "***Dry run option enabled***" + color.END)
        print(color.PURPLE + "Dry run deleting alias %s on %s" % (alias_name, lambda_name) + color.END)
        return True
      else:
        try:
          delete_alias = client.delete_alias(
              FunctionName='%s' % lambda_name,
              Name='%s' % alias_name
          )
          print("Alias successfully deleted")
          return True
        except ClientError as error:
          print(error.response['Error']['Message'])
    else:
      print("That alias does not exist, please check the list of existing aliases and try again")
  else:
    print("No aliases found..")

def alias_update():
  lambda_name = json_parser()["initializers"]["name"]

  versions = client.list_versions_by_function(
                    FunctionName='%s' % lambda_name,
                  )

  version_json = json.dumps(versions, indent=4)
  load_json = json.loads(version_json)
  versions = load_json['Versions']
  avail_versions = []

  for version in versions:
    if version['Version'] != 0:
      version = version['Version']
      if version == "$LATEST":
        version = 0
        avail_versions.append(version)
      else:
        avail_versions.append(version)

  alias = client.list_aliases(
    FunctionName='%s' % lambda_name,
    )

  dump_json = json.dumps(alias, indent=4) 
  load = json.loads(dump_json)

  aliases = []

  for names in load['Aliases']:
    print("Function Version: '%s' has alias: '%s'" % (names['FunctionVersion'], names['Name']))     
    aliases.append(names['Name'])
  print("\n")

  if len(aliases) != 0:
    if 'alias' in json_parser()['initializers']:
      alias_name = json_parser()['initializers']['alias']
    elif ARGS.alias:
      alias_name = ARGS.alias
    else:
      alias_name = input("What alias would you like to update? ")

    if ARGS.publish:
      largest = max(avail_versions, key=int)
      if largest == 0:
        version_update = '$LATEST'
      else:
        version_update = largest
    else:
      for version in avail_versions:
        print("Version: " + str(version))

      version_update = input("What version would you like to assign the update alias to? ")

    if alias_name in aliases:
      if version_update in avail_versions:
        if version_update == 0:
          version_update == "$LATEST"
        else:
          pass
        if ARGS.dry_run:
          print(color.PURPLE + "***Dry run option enabled***" + color.END)
          print(color.PURPLE + "Would have updated update alias '%s' on version '%s' on lambda '%s'" % (alias_name, version_update, lambda_name) + color.END)
          return True
        else:
          try:
            update_alias = client.update_alias(
                            FunctionName='%s' % lambda_name,
                            Name='%s' % alias_name,
                            FunctionVersion='%s' % version_update,
                          )
            if update_alias['ResponseMetadata']['HTTPStatusCode'] == 200:
              print("Lamda '%s' version '%s' alias '%s' has been updated!" % (lambda_name, version_update, alias_name))
              return True
            else:
              return False
          except ClientError as error:
            print(error.response['Error']['Message'])
      else:
        print("Version not found..")
    else:
      print("No aliases found...")
