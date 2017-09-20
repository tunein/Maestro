import boto3
#import maestro.lambda_config as lambda_config
import sys
import json
import zipfile
import os
from botocore.exceptions import ClientError
#from maestro.cli import ARGS

client = boto3.client('lambda')
#DOC = ARGS.filename
#PAYLOAD = ARGS.payload

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
'''
def json_parser():
  with open('%s' % DOC) as json_data:
    read = json.load(json_data)
    return read
    return True
  print("No json document to read.. Please enter a valid json document")
'''
def list_lambdas():
  #lambda_name = json_parser()["initializers"]["name"]
  lambda_name = "example"
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

def list_aliases():
  #lambda_name = json_parser()["initializers"]["name"]
  lambda_name = "example"

  alias = client.list_aliases(
    FunctionName='%s' % lambda_name,
    )

  dump_json = json.dumps(alias, indent=4) 
  load = json.loads(dump_json)

  aliases = []

  for names in load['Aliases']:    
    aliases.append(names['Name'])

  return aliases

def test_invoke():
  alias = "dev"
  invoke_type = "Event"
  payload = ""
  function_arn = list_lambdas()
  avail_aliases = list_aliases()

  if alias:
    if alias in avail_aliases:
      qualifier = alias
      function_arn = "%s:%s" % (function_arn, alias)
      print(function_arn)
  else:
    print("Available aliases:")
    for item in avail_aliases:
      print("Alias: %s" % item)
    ask = input("What alias would you like to invoke? ")

    if ask in avail_aliases:
      qualifier = ask

  if invoke_type:
    invocator = invoke_type
  '''
  if payload:
    pay_load = payload
  else:
    payload = ''
  '''
  response = client.invoke(
                      FunctionName=function_arn,
                      InvocationType=invocator,
                      LogType='Tail',
                      #Payload=open(pay_load, 'rb').read(),
                      Qualifier=qualifier
                    )
  if response['StatusCode'] == 202:
    print(response)

test_invoke()