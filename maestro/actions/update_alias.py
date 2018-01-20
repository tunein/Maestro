#External libs
import os
import sys

#Get relevant modules
from maestro.providers.aws.check_existence import check
from maestro.providers.aws.alias import alias_update

def update_alias_action(name, alias, dry_run=False, publish=False, weight=False):
    '''
    Updates an alias for the given function, first we check to see if the lambda exists, then we update alias

    args:
        name: name of the lambda
        alias: name of the alias we're updating
        dry_run: boolean, if true no action occurs, just printing
        weight: boolean, if true we're weight shifting an alias across two versions
    '''
    print('Checking to see if Lambda exists')
    if check(name):
        print('Lambda found! Attempting to update alias %s' % alias)

        #Run the destroy function
        alias_update(lambda_name=name, update_alias=alias, dry_run=dry_run, publish=publish, weight=weight)

    else:
        print('Lambda not found!')
        sys.exit(1)