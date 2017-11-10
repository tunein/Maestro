#External libs
import boto3
import sys
import json
import os
from time import gmtime, strftime
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
iam = boto3.resource('iam')
roles = boto3.client('iam')

#Establish easy to read variables for stuff from config file
AVAIL_RUNTIMES = lambda_config.AVAIL_RUNTIMES
AVAIL_ACTIONS = lambda_config.AVAIL_ACTIONS

def file_type(doc):
    '''
    Validates we have a doc with the extension json
    
    args:
        doc: the document we'd like to validate
    '''
    print(color.CYAN + "validating file type..." + color.END)
    if len(doc)>0:
        if doc.lower().endswith('.json'):
            return True
        return False
    print(color.RED + "Please enter a valid json document after your action" + color.END)

def validate_action(current_action):
    '''
    Validates the action we specified is in the list of available actions:

    args:
        current_action: action retrieved from CLI (create, delete, etc)
    '''
    if any(action in current_action for action in AVAIL_ACTIONS):
        return True
    print(color.RED + "Not a valid action" + color.END)

def validate_runtime(config_runtime):
    '''
    Validates that the language we want to use is supported by AWS

    args:
        config_runtime: runtime (nodejs, python, .NET, etc) pulled from config file
    '''
    print(color.CYAN + "validating runtime %s..." % config_runtime + color.END)
    if any(runtime in config_runtime for runtime in AVAIL_RUNTIMES):
        return True
    print(color.RED + "Not a valid runtime" + color.END)

def validate_role(role):
    '''
    Validates the role exists in our AWS account in the region we are working in 

    args:
        role: the name of a valid role in AWS, retrieved from the config file
    '''
    print(color.CYAN + "validating role %s..." % role + color.END)
    data = iam.role_name=role
    if len(data)>0:
        return True
    print(color.RED + "invalid role" + color.END)  

def validate_timeout(timeout):
    '''
    Validates the timeout specified is within the bounds that AWS accepts

    args:
        timeout: integer retrieved from config file
    '''
    acceptable_range = range(1,301)
    if timeout in acceptable_range:
        return True
    print(color.RED + "Timeout should between between 1 and 300 seconds, please adjust" + color.END)

######### Main Entry point ##########
def validation(doc, current_action, config_runtime, role, timeout):
    '''
    This is the main entrypoint to this module, for ease of use in calling it from elsewhere
    Runs everything down in a row to validate all of our actions
    '''
    if file_type(doc):
        if validate_action(current_action):
            if validate_runtime(config_runtime):
                if validate_role(role):
                    if validate_timeout(timeout):
                        return True