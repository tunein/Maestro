#External libs
import os
import sys

#Get relevant modules
from maestro.providers.aws.check_existence import check
from maestro.providers.aws.invoke import main as invoke

def invoke_action(name,  invoke_type, payload, version=False, alias=False):
    '''
    Invokes a lambda with the given JSON payload. payload and invoke_type are specified by the CLI.
    First thing we do is check to make sure the lambda exists

    args:
        name: name of the lambda
        version: version we're invoking (if applicable)
        alias: alias we're invoking (if applicable)
        invoke_type: taken from the cli, options are Event, RequestResponse, and DryRun
        payload: json payload from a file
    '''
    print('Checking to see if the lambda exists')
    if check(name):
        print('Found lambda %s attempting to invoke' % name)

        invoke(lambda_name=name, version=version, alias=alias, invoke_type=invoke_type, payload=payload)
    else:
        print('No lambda found, please check your configuration and try again')
        sys.exit(1)