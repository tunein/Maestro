import boto3
import maestro.lambda_config as lambda_config
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
  print("No json document to read.. Please enter a valid json document")

def alias_creation():
  lambda_name = json_parser()["initializers"]["name"]

  get_alias_name = input("What would you like this alias to be called? ")
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

  function_version = input("What version would you like to create an alias for? ")
  
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
    except ClientError:
      print(message)
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
    alias_name = input("What alias would you like to delete? ")

    if alias_name in aliases:
      try:
        delete_alias = client.delete_alias(
            FunctionName='%s' % lambda_name,
            Name='%s' % alias_name
        )
        print("Alias successfully deleted")
        return True
      except ClientError:
        print(message)
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
  print("Available Versions")
  for version in versions:
    if version['Version'] != 0:
      print('version: %s' % version['Version'])
      avail_versions.append(version['Version'])

  if len(aliases) != 0:
    alias_name = input("What alias would you like to update? ")
    version_update = input("What version would you like to assign the update alias to? ")

    if alias_name in aliases:
      if version_update in avail_versions:
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
        except ClientError:
          print(message)
      else:
        print("Version not found..")
    else:
      print("No aliases found...")