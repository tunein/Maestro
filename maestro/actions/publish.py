import os
import sys

from maestro.providers.aws.check_existence import check
from maestro.providers.aws.publish_lambda import publish

def publish_action(name, version_description):
    '''
    Publishes a new version of the specified lambda. If the version description doesn't exist from the CLI
    it defaults to printing the date + time in UTC as the version description. First thing we do is check to
    see if the lambda exists

    args:
        name: name of the lambda we're publishing a new version of 
        version_description: description of the version (datetime or user specified)
    '''
    print('Checking to see if lambda exists')
    
    if check(name):
        print('Attempting to publish new version of lambda %s with descriptiong %s' % (name, version_description))

        publish(lambda_name=name, version_description=version_description)
    else:
        print('Lambda does not exists, please check your configuration and try again')
        sys.exit(1)