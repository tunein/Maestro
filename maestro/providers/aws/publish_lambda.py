#External libs
import boto3
import sys
import os
from time import gmtime, strftime
from botocore.exceptions import ClientError

#Establish our boto resources
client = boto3.client('lambda')

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

def publish(lambda_name, version_description=False): 
    '''
    Publishes a new version of the lambda, the number is controlled by AWS

    args:
        lambda_name: name of the lambda, retrived from config file
        version_description: allows users to pass their own version description, most like a git hash, defaults to current time in UTC
    ''' 
    try:
        if version_description:
            version_descript = version_description
            print("Description: %s" % version_descript)
        else:
            version_descript = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
            print("Description: %s" % version_descript)

        publish = client.publish_version(
            FunctionName='%s' % lambda_name,
            Description=version_descript
            )
        if publish['ResponseMetadata']['HTTPStatusCode'] == 201:
            print(color.CYAN + "Successfully published %s version %s" % (lambda_name, publish['Version']) + color.END)
            return 0
        else:
            return False    
    except ClientError as error:
        print(color.RED + error.response['Error']['Message'] + color.END)
        sys.exit(1)
