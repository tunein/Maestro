#External libs
import os
import sys

#Get relevant modules
from maestro.providers.aws.check_existence import check
from maestro.providers.aws.update_lambda_code import update_code
from maestro.providers.aws.s3_backup import main as s3_backup

def update_code_action(name, dry_run=False, publish=False, no_pub=False, bucket_name=False):
    '''
    Updates the code of a given lambda function, options to dry run, publish a version, or NOT publish a version
    First thing we do is check to see if the lambda is there..

    args:
        name:
        dry_run:
        publish:
        no_pub:
        bucket_name: 
    '''
    print('Checking to see if the lambda exists')
    if check(name):
        print('Found lambda %s! Attempting to update code' % name)
        
        update = update_code(lambda_name=name, dry_run=dry_run, publish=publish, no_pub=no_pub)
        
        #Check to see if they want to backup
        if bucket_name:
            s3_backup(lambda_name=name, bucket_name=bucket_name, dry_run=dry_run)
        else:
            pass
    else:
        print('Lambda not found!')
        sys.exit(1)