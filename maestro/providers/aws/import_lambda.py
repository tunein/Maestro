#External libs
import ast
import boto3
import json
import sys
import os
from botocore.exceptions import ClientError

#Establish our boto resources
client = boto3.client('lambda')
session = boto3.session.Session()
region = session.region_name
ec2Client = boto3.client('ec2')

def import_config(lambda_name, alias=False):
    '''
    Uses the lambda name to grab existing lambda configuration
    and import it into a config file

    args:
        lambda_name: the name of the lambda you want to import
        alias: the alias, defaults to $LATEST if not present
    '''
    print('Attempting to import configuration')
    #Create an empty config dict, start with the bare minimum
    config_dict = { 
                    "initializers": {
                        "name": "",
                        "description": "",
                        "region": region,
                        "handler": "",
                        "role": ""
                    },
                    "provisioners": {
                        "runtime": "",
                        "timeout": 0,
                        "mem_size": 0
                    }
                }

    #If the user didn't pass an alias we want to use $LATEST
    if not alias:
        alias_used = '$LATEST'
    else:
        alias_used = alias

    try:
        lambda_config = client.get_function(
                            FunctionName=lambda_name,
                            Qualifier=alias_used
                        )

        #Set a variable to make things readable later
        config = lambda_config['Configuration']
    except ClientError as error:
        print(error.response)
        sys.exit(1)
    else:
        #Check to make sure there is a config there
        #print(json.dumps(config, indent=4))
        if 'FunctionName' in config:
            #Grab our initializers
            config_dict['initializers']['name'] = config['FunctionName']
            config_dict['initializers']['handler'] = handler = config['Handler']
            config_dict['initializers']['description'] = config['Description']
            config_dict['initializers']['role'] = config['Role'].split('/')[-1]
            
            #Grab our provisioners
            config_dict['provisioners']['timeout'] = config['Timeout']
            config_dict['provisioners']['mem_size'] = config['MemorySize']
            config_dict['provisioners']['runtime'] = config['Runtime']

            #VPC Work
            sg_ids = config['VpcConfig']['SecurityGroupIds']

            if len(sg_ids) != 0:
                vpc_id = config['VpcConfig']['VpcId']
                config_dict['vpc_setting'] = {"vpc_name": vpc_id, "security_group_ids": sg_ids}     
            else:
                pass
            
            #Tracing config
            trace_config = config['TracingConfig']

            if trace_config['Mode'] != "PassThrough":
                config_dict['initializers']['tracing_mode'] = trace_config['Mode'].lower()
            else:
                pass

            if 'DeadLetterConfig' in config:
                #Split DLQ config so we can grab things easily
                dead_letter_split = config['DeadLetterConfig']['TargetArn'].split(':')

                config_dict['dead_letter_config'] = {"type": dead_letter_split[2], "target_name": dead_letter_split[-1]}
            else:
                pass

            #Variables
            if 'Environment' in config:
                config_dict['variables'] = config['Environment']['Variables']
            else:
                pass

            #Write the alias if needed
            if alias_used != "$LATEST":
                config_dict['initializers']['alias'] = alias
            else:
                pass

            #Set a variable for the ARN
            true_arn = config['FunctionArn'].split(':')[:7]
            function_arn = ":".join(true_arn)
        else:
            print("No Lambda found! Please check your config")
    finally:
        return config_dict, function_arn

def import_triggers(lambda_name, alias=False):
    '''
    Uses the lambda name to grab triggers from existing lambda config
    and import it into a config file

    args:
        lambda_name: 
        alias: 
    '''
    print("Attempting to retrieve lambda triggers")
    try:
        if not alias:
            get_lambda_policy = client.get_policy(
                        FunctionName=lambda_name
                    )
        else:
            get_lambda_policy = client.get_policy(
                            FunctionName=lambda_name,
                            Qualifier=alias
                        ) 
    except ClientError as error:
        print("No policy found")
        principal = ''
        resource = ''
    else:
        policy = ast.literal_eval(get_lambda_policy['Policy'])
        statement_dict = policy['Statement'][0]
        principal = statement_dict['Principal']['Service'].split('.')[0]
        resource = statement_dict['Condition']['ArnLike']['AWS:SourceArn'].split(":")[-1]
    finally:
        return principal, resource

def get_sg_name(sg_id):
    '''
    Grabs the NAME of the security groups, we want them because they are
    friendlier to read than the sg code

    args:
        sg_id: the id of the security group, returned from import_config
    '''
    print('Attempting to retrieve security group names')
    try:
        sg_info = ec2Client.describe_security_groups(
                    GroupIds=sg_id
                )
        group_info = sg_info['SecurityGroups'][0]
    except ClientError as error:
        print(error.response)
        sys.exit(1)
    finally:
        print("Retrieved name for groups %s" % group_info['GroupName'])
        return group_info['GroupName']

def get_vpc_name(vpc_id):
    '''
    Grabs the NAME of the VPC

    args:
        vpc_id: the id the VPC, returned from import_config
    '''
    print('Attempting to retrieve VPC name')
    try:
        vpc_info = ec2Client.describe_vpcs(
                        VpcIds=[vpc_id]
                    )
        vpc_info = vpc_info['Vpcs'][0]
    except ClientError as error:
        print(error.response)
        sys.exit(1)
    else:
        tags = vpc_info['Tags'][0]
        
        if tags['Key'] == 'Name':
            name = tags['Value']
        else:
            print("No VPC found, make sure your VPC is tagged 'Key': 'Name', 'Value': 'Your-VPC'")
            sys.exit(1)
    finally:
        print('Retrieved VPC name %s' % name)
        return name

def get_tags(lambda_arn):
    '''
    Grabs a tags dict from the current lambda

    args:
        lambda_arn: the arn returned from the import config function
    '''
    print('Attempting to retrieve tags')
    try:
        tags = client.list_tags(Resource=lambda_arn)
        tags = tags['Tags']
    except ClientError as error:
        print(error.response)
        sys.exit(1)
    finally:
        return tags

########### Entrypoint ###########
def import_lambda(lambda_name, alias):
    '''
    The main entry point of the module

    args:
        lambda_name: the name of the lambda
        alias: alias of the lambda
    '''
    config_dict, lambda_arn = import_config(lambda_name=lambda_name, alias=alias)
    tag_dict = get_tags(lambda_arn)

    if len(tag_dict) != 0:
        config_dict['tags'] = tag_dict

    if 'vpc_setting' in config_dict:
        config_dict['vpc_setting']['vpc_name'] = get_vpc_name(config_dict['vpc_setting']['vpc_name'])
        config_dict['vpc_setting']['security_group_ids'] = get_sg_name(config_dict['vpc_setting']['security_group_ids'])

    trigger_method, trigger_source = import_triggers(lambda_name=lambda_name, alias=alias)
    
    if len(trigger_method) != 0:
        config_dict['trigger'] = {"method": trigger_method, "source": trigger_source}
    
    return config_dict