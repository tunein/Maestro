#External libs
import boto3
import sys
import json
import os

#Establish our boto resources
iam = boto3.resource('iam')

def get_arn(config_role):
    '''
    Returns the arn of the role specified in config file

    args:
        config_role: role retrieved from the config file
    '''
    role = iam.Role(config_role)
    arn = role.arn
    return arn