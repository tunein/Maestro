#External libs
import os
import sys

#Get relevant modules
from maestro.providers.aws.check_existence import check
from maestro.providers.aws.alias import alias_destroy

def delete_alias_action(name, alias, dry_run):
    '''
    Deletes an alias for the given function, first we check to see if the lambda exists, then we delete alias

    args:
        name: name of the lambda
        alias: name of the alias we're deleting
        dry_run: boolean, if yes no action occurs, just printing
    '''
    print('Checking to see if Lambda exists')
    if check(name):
        print('Lambda found! Attempting to delete alias %s' % alias)

        #Run the destroy function
        alias_destroy(lambda_name=name, del_alias=alias, dry_run=dry_run)

    else:
        print('Lambda not found!')
        sys.exit(1)