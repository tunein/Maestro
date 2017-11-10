#External libs
import boto3
import sys
import json
import zipfile
import os
import base64
from botocore.exceptions import ClientError

#Our modules
import maestro.lambda_config as lambda_config

#This is only here for printing pretty colors
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

#Establish our boto resources
client = boto3.client('lambda')

#Establish easy to read variables for stuff from config file
test_invoke_type = lambda_config.TEST_INVOKE_TYPE

def get_lambda_arn(lambda_name):
    '''
    grabs the arn of the lambda we want to invoke

    args:
        lambda_name: the name of the lambda, pulled from the config file
    '''
    try:
        repsonse = client.get_function(FunctionName=lambda_name)

        dump = json.dumps(repsonse, indent=4)
        load = json.loads(dump)

        arn = load['Configuration']['FunctionArn']

        return arn
    except ClientError as error:
        print(color.RED + error.response['Error']['Message'] + color.END)

def list_aliases(lambda_name):
    '''
    generates a list of available aliases for the functino identified with "lambda_name"
    used for validation on the "test_invoke" function

    args:
        lambda_name: the name of the lambda, pulled from the config file
    '''
    alias = client.list_aliases(
        FunctionName='%s' % lambda_name,
        )

    dump_json = json.dumps(alias, indent=4) 
    load = json.loads(dump_json)

    aliases = []

    for names in load['Aliases']:    
        aliases.append(names['Name'])

    return aliases

def list_versions(lambda_name):
    '''
    generates a list of available versions for the lambda identified with "lambda_name"
    used for validation on the "test_invoke" function

    args:
        lambda_name: the name of the lambda, pulled from the config file

    '''
    versions = client.list_versions_by_function(
                                        FunctionName='%s' % lambda_name,
                                    )

    version_json = json.dumps(versions, indent=4)
    load_json = json.loads(version_json)
    versions = load_json['Versions']
    avail_versions = []

    for version in versions:
        if version['Version'] != 0:
            avail_versions.append(version['Version'])

    return avail_versions

def test_invoke(function_arn, avail_aliases, avail_versions, *, version=False, alias=False, invoke_type=False, payload=False):
    '''
    This is the function that actually invokes the lambda
    
    It runs last after the collection of available aliases and versions are generated.

    args:
        function_arn: arn of the function you're invoking, generated from the list lambdas function
        avail_aliases: list of aliases for the function, validates alias passed in CLI
        avail_versions: list of versions for the function, validates version passed in CLI
        version: version of the lambda the user would like to invoke
        alias:
        invoke_type:
        payload:
    '''
    if version:
        if version in avail_versions:
            if version == "LATEST":
                function_arn = "%s" % function_arn
            else:
                function_arn = "%s:%s" % (function_arn, version)
    else:
        if alias:
            if alias in avail_aliases:
                function_arn = "%s:%s" % (function_arn, alias)
        else:
            print("Available aliases:")
            for item in avail_aliases:
                print("Alias: %s" % item)
                for version in avail_versions:
                    print("Version: %s" % version)
            ask = input("What alias or version would you like to invoke? ")

            if ask in [avail_aliases, avail_versions]:
                function_arn = "%s:%s" % (function_arn, ask)

    if invoke_type:
        if invoke_type in test_invoke_type:
            invocator = invoke_type
    else:
        ask_invoke = input("Please enter an invocation type (Event, RequestResponse, DryRun): ")
        if ask_invoke in test_invoke_type:
            invocator = ask_invoke

    if payload:
        pay_load = payload
    else:
        get_file = input("Input a valid json filename for payload: ")
        pay_load = os.getcwd() + "/%s" % get_file

    try:
        response = client.invoke(
                                                FunctionName=function_arn,
                                                InvocationType=invocator,
                                                LogType='Tail',
                                                Payload=open(pay_load, 'rb').read(),
                                            )
        if response['StatusCode'] in [200, 202, 204]:
            try:
                coded_response = response['LogResult']
                decoded_response = base64.b64decode(coded_response)
                byte_to_string = decoded_response.decode("utf-8")
                print(color.CYAN + "Invoked successfully! Logs below" + color.END)
                print(color.DARKCYAN + byte_to_string + color.END)
                return True
            except:
                print(color.CYAN + "Invoked successfully!" + color.END)
                return True
    except ClientError as error:
        print(color.RED + error.response['Error']['Message'] + color.END)

########## Main Entrypoint ############
def main(lambda_name, version, alias, invoke_type, payload):
    '''
    To simplify usage, this is the main entry point of this module

    args:
        lambda_name: name of the lambda you're invoking, pulled from config file
        version: version of the lambda, defaults to $LATEST, pulled from CLI args
        alias: alias of the lambda, defautls to none (aka $LATEST), pulled from CLI args
        invoke_type: invocation type (event, request response, dry run), pulled from CLI args
        payload: json payload to test the lambda with, pulled from CLI args
    '''
    function_arn = get_lambda_arn(lambda_name)
    avail_aliases = list_aliases(lambda_name)
    avail_versions = list_versions(lambda_name)
    invoke = test_invoke(function_arn=function_arn, 
                                                avail_aliases=avail_aliases, 
                                                avail_versions=avail_versions,
                                                version=version,
                                                alias=alias,
                                                invoke_type=invoke_type,
                                                payload=payload
                                            )