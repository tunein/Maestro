#External libs
import boto3
import sys
import json
import os
from botocore.exceptions import ClientError

#Establish our boto resources
client = boto3.client('lambda')

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


def check(lambda_name):
    '''
    Checks to see if the lambda exists already, if it does, the user will be prompted to use 'update-code' action

    args:
        lambda_name: name of the lambda, retrieved from config file
    '''
    try:
        function = client.get_function(FunctionName=lambda_name)
        if len(function) > 0:
            return True
        else:
            return False
    except ClientError as error:
        print(error.response)


def check_alias(lambda_name, alias):
    '''
    Checks our lambda to ensure the alias we want to import from exits
    
    args:
        lambda_name: name of the lambda we're checking
        alias: name of the alias we're checking
    '''
    try:
        alias = client.get_alias(FunctionName=lambda_name, Name=alias)
    except ClientError as error:
        print(error.response['Error']['Message'])
        sys.exit(1)
    else:
        print("Alias located successfully!")
    finally:
        return True