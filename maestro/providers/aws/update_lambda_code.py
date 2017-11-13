#External libs
import boto3
import sys
import json
import os
from botocore.exceptions import ClientError

#Get our config
import maestro.config.lambda_config as lambda_config

#Get other necessary AWS modules
from maestro.providers.aws.role_arn import get_arn
from maestro.providers.aws.vpc_location import main as vpc_location
from maestro.providers.aws.security_groups import security_groups
from maestro.providers.aws.dlq import get_sns_arn
from maestro.providers.aws.dlq import get_sqs_arn

#Get zip helper function
from maestro.helpers.zip_function import zip_function

#Establish our boto resources
client = boto3.client('lambda')

#Establish easy to read variables for stuff from config file
TRACING_TYPES = lambda_config.TRACE_TYPES
ACCEPTED_PROMPT_ACTIONS = lambda_config.ACCEPTED_PROMPT_ACTIONS

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

def update_code(lambda_name, dry_run=False, publish=False, no_pub=False):
    '''
    Updates the code of a specific function, this is usually run in tandem with update alias and/or publish

    args:
        lambda_name: name of the lamdba, retrieved from config file
        dry_run: CLI arg, used if the user wants to just see what would happen
        publish: boolean CLI arg, defaults to false, if true publishes a new version (when applicable)
        no_pub: publishes code to "$LATEST", used for updating code and running integration tests
    '''
    archive_name = os.getcwd() + '/%s.zip' % lambda_name  

    if zip_function(lambda_name):
        print(color.CYAN + "Attempting to update lambda..." + color.END)

        if dry_run:
            print(color.PURPLE + "***Dry Run option enabled, running dry run code-update***" + color.END)
            run = True
        else:
            run = False

        if publish:
            answer = True
        elif no_pub:
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
                if dry_run:
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
