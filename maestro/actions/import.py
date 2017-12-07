#External libs
import os
import json
import sys

#Our modules
from maestro.providers.aws.import_lambda import import_lambda

#Get the config file that has our allowances 
import maestro.config.lambda_config as lambda_config

def import_action(filename):
    '''
    Calls the import module for AWS provider to collect the configuration
    of the lambda specified in the args. Alias by default is false.

    args:
        lambda_name: the name of the lambda of which we want to import
        alias: the name of the specific alias we want to import
    '''
    #Prompt the user to input the lambda and (optionally) alias they'd like the import
    lambda_name = input("What is the name of the lambda you'd like to import? ")
    alias_prompt = input("Are you importing a configuration from an alias? (y/n): ")

    if alias_prompt in lambda_config.ACCEPTED_PROMPT_ACTIONS:
        if alias_prompt == 'y':
            alias = input("What alias would you like to import from? ")
        else:
            alias = False
    else:
        print("No valid answer found, exiting")
        sys.exit(1)

    #to do: add check to make sure lambda and alias exist prior to attempting to import

    #Call the import function
    configuration = import_lambda(lambda_name=lambda_name, alias=alias)

    #Create a file, we'll call it the name of the lambda
    cwd = os.getcwd()
    full_path = os.path.join(cwd, filename)

    #Dump the config we retrieved from AWS into the file
    f = open(full_path, 'w')
    f.write(json.dumps(configuration, indent=4))
    f.close()