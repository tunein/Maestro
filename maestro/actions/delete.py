#External libs
import os
import sys

#Get relevant modules
from maestro.providers.aws.check_existence import check
from maestro.providers.aws.delete_lambda import delete

def delete_action(name, dry_run):
    '''
    Deletes the specified lambda function, has a dry run option just to make sure it will work before actually
    going for it. The first thing we do is check if the specified lambda exists

    args:
        name: name of the lambda we're deleting
        dry_run: boolean, if true only prints what would happen
    '''
    print('Checking to see if lambda exists')

    if check(name):
        print('Lambda exists, attempting to delete %s' % name)

        delete(lambda_name=name, dry_run=dry_run)
    else:
        print('No lambda found, exiting')
        sys.exit(1)