#External libs
import boto3
import sys
import json
import os
from botocore.exceptions import ClientError

#Get our config
import maestro.config.lambda_config as lambda_config

#Get other necessary AWS modules
from maestro.providers.aws.role_arn import get_arn
from maestro.providers.aws.vpc_location import main as vpc_location
from maestro.providers.aws.security_groups import security_groups
from maestro.providers.aws.dlq import get_sns_arn
from maestro.providers.aws.dlq import get_sqs_arn

#Establish our boto resources
client = boto3.client('lambda')

#Establish easy to read variables for stuff from config file
TRACING_TYPES = lambda_config.TRACE_TYPES

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

def get_lambda_arn(lambda_name):
    '''
    Retrieves unique amazon resource name (ARN) of lambda, for usage in the 'invoke_action' function

    args:
            lambda_name: the name of the lambda, retrieved from the config file
    '''
    try:
        repsonse = client.get_function(FunctionName=lambda_name)

        dump = json.dumps(repsonse, indent=4)
        load = json.loads(dump)

        arn = load['Configuration']['FunctionArn']

        return arn
    except ClientError as error:
        print(color.RED + error.response['Error']['Message'] + color.END)

def update_config(lambda_name, handler, description, timeout, mem_size, runtime, role, vpc_setting=False, config_vpc_name=False, 
                 config_security_groups=False, new_tags=False, variables=False, dead_letter_config=False, tracing_mode=False):
    '''
    Updates the configuration of the specified lambda. It does NOT update the code but updates the core
    configuration of the lambda, if you are pushing a major code change it's recommended to run this first

    args:
        lambda_name: name of the lambda, retrieved from config file
        handler: main entrypoint of your code module.function_name, retrieved from config file
        description: a brief description of your lambda, retrieved from config file
        timeout: integer, in seconds, for how long the lambda can run
        mem_size: integer, in mb, for how much memory the lambda can consume
        runtime: runtime (python, node, .NET ect) of the lambda, retrieved from config
        vpc_setting: boolean, if yes grab vpc name and security group ids from config
        vpc_name: vpc name from config file
        security_group_ids: security group names from config file
        new_tags: a dictionary of tags copied from config file
        variables: dictionary of environment variables for the lambda, grabbed from config file
        dead_letter_config: boolean, if yes grab dlq type and name from config
    '''
    #Set up two blank arrays for collecting subnet ids and security group ids
    subnet_ids = []
    security_group_id_list = []

    if vpc_setting:
        subnets = vpc_location(config_vpc_name)
        subnet_ids.extend(subnets)

        groups = security_groups(config_security_groups)
        security_group_id_list.extend(groups)
    else:
        pass

    #Update the tags from the tag dictionary
    tags = {}

    if new_tags:
        tags.update(new_tags)
        try:
            generate_tags = client.tag_resource(
                                                Resource=get_lambda_arn(lambda_name),
                                                Tags=new_tags
                                            )
        except ClientError as error:
            print(color.RED + error.response['Error']['Message'] + color.END)
    else:
        pass

    #Create a dictionary for vpc config
    if len(subnet_ids)>0:
        vpc_config = {
                                    'SubnetIds': subnet_ids,
                                    'SecurityGroupIds': security_group_id_list
                                }
    else:
        vpc_config = { }

    #Set up environment variables
    if variables:
        env_vars = variables
    else:
        env_vars = { }

    #Get SNS/SQS information and add it to the target arn dictionary for DLQ config
    target_arn = { }

    if dead_letter_config:
        dlq_type = dlq_type
        dlq_name = dlq_name
        if dlq_type == 'sns':
            arn = get_sns_arn(dlq_name)
            target_arn.update({'TargetArn': arn})
        elif dlq_type == 'sqs':
            arn = get_sqs_arn(dlq_name)
            target_arn.update({'TargetArn': arn})
        else:
            raise RuntimeError('No valid DLQ type found')
    else:
        print('No DLQ resource found, passing')
        pass

    #Set up tracing, if applicable
    trace_type = { }

    if tracing_mode:
        mode = tracing_mode
        if mode in TRACING_TYPES:
            if mode == "active":
                capmode = "Active"
                trace_type.update({'Mode': capmode})
            elif mode == "passthrough":
                capmode = "PassThrough"
                trace_type.update({'Mode': capmode})
        else:
            raise RuntimeError('No valid trace mode found')
    else:
        trace_type = {'Mode': 'PassThrough'}

    #Update the lambda config, the big payoff!
    try:
        update_configuration = client.update_function_configuration(
            FunctionName=lambda_name,
            Role='%s' % get_arn(role),
            Handler=handler,
            Description=description,
            Timeout=timeout,
            MemorySize=mem_size,
            VpcConfig=vpc_config,
            Runtime=runtime,
            Environment={
                    'Variables': env_vars
                },
            DeadLetterConfig=target_arn,
            TracingConfig=trace_type
            )
        if update_configuration['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False
    except ClientError as error:
        print(color.RED + error.response['Error']['Message'] + color.END)
