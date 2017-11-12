#External libs
import boto3
import sys
import os
import json
import ast
from botocore.exceptions import ClientError

#Establish our boto resources
client = boto3.client('lambda')

def json_helper(json_dict, section_name):
    output = json_dict.get(section_name, None)

    if output is None:
        output = False

    return output

def get_lambda_policy(name, alias=False, version=False):
    '''
    Gets the policy of the current lambda, this is used in the update config action to check if the 
    trigger already exists

    args:
        name: name of the lambda
        alias: alias you're lookin to add a trigger to
        version: version you're looking to ad a trigger to
    '''
    if alias:
        qualifer = alias
    elif version:
        qualifer = version
    else:
        qualifer = ''

    try:
        response = client.get_policy(FunctionName=name, Qualifier=qualifer)

        dump = json.dumps(response, indent=4)
        loads = json.loads(dump)

        policy = ast.literal_eval(loads['Policy'])

        policy_dictionary = policy['Statement'][0]

        if json_helper(policy_dictionary, 'Resource'):
            func_alias = policy['Statement'][0]['Resource'].split(':')[7]

        if json_helper(policy_dictionary, 'Condition'):
            trigger_method = policy['Statement'][0]['Condition']['ArnLike']['AWS:SourceArn'].split(':')[2]
            trigger_source = policy['Statement'][0]['Condition']['ArnLike']['AWS:SourceArn'].split(':')[5]

        return [func_alias, trigger_method, trigger_source]
    except ClientError as error:
        print(error.response)
        return False