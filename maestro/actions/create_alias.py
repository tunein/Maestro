import os
import sys

from maestro.providers.aws.check_existence import check
from maestro.providers.aws.alias import alias_creation

def create_alias_action(name, alias, dry_run=False, publish=False):
    '''
    Creates an alias for the given function, first we check to see if the lambda exists, then we create alias

    args:
        name: name of the lambda
        alias: name of the alias we're creating
        dry_run: boolean, if yes no action occurs, just printing
        publish: boolean, if yes we publish a new version for this alias
    '''
    print('Checking to see if Lambda exists')
    if check(name):
        print('Lambda found! Attempting to create alias %s' % alias)

        #Run the create function
        alias_creation(lambda_name=name, new_alias=alias, dry_run=dry_run, publish=publish)

    else:
        print('Lambda not found!')
        sys.exit(1)