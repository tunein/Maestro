import os
import sys

from maestro.providers.aws.check_existence import check
from maestro.providers.aws.publish_lambda import publish

def publish_action(name, version_description):
    print('Checking to see if lambda exists')
    if check(name):
        print('Attempting to publish new version of lambda %s with descriptiong %s' % (name, version_description))

        publish(lambda_name=name, version_description=version_description)
    else:
        print('Lambda does not exists, please check your configuration and try again')
        sys.exit(1)