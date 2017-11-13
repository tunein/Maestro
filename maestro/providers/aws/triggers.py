#External libs
import boto3
import sys
import json
import os
from datetime import datetime
from botocore.exceptions import ClientError

#Get our config
import maestro.config.lambda_config as lambda_config

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

#Establish our boto resources
client = boto3.client('lambda')
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
sns_client = boto3.client('sns')
cloudwatch_client = boto3.client('events')
my_session = boto3.session.Session()
region = my_session.region_name

#Establish easy to read variables for stuff from config file
REGIONS = lambda_config.REGIONS
ACL_ANSWERS = lambda_config.ACL_ANSWERS
EVENT_TYPES = lambda_config.EVENT_TYPES
principals = lambda_config.PRINCIPALS

def check_s3(invoke_source):
    '''
    Checks to see if the specified bucket exists

    args:
        invoke_source: the name of the s3 bucket, as specified in either CLI arg or config file
    '''
    bucket_name = invoke_source
    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
        print("Bucket found!")
        return True
    except ClientError as error:
        print(error.response['Error']['Message'])
        sys.exit(1)

def get_sns_arn(invoke_source):
    '''
    Checks SNS to ensure topic exists, then returns unique amazon resource name (ARN)

    args:
        invoke_source: name of the sns topic as specified in either CLI arg or config file
    '''
    topic_name = invoke_source

    list_of_topics = []
    try:
        existing_topics = sns_client.list_topics()
        dumper = json.dumps(existing_topics, indent=4)
        loader = json.loads(dumper)
        topics = loader['Topics']

        for obj in topics:
            for key, value in obj.items():
                list_of_topics.append(value)

        for item in list_of_topics:
            if topic_name in item:
                return item

    except ClientError as error:
        print(json.dumps(error.response, indent=4))

def get_cloudwatch_arn(invoke_source):
    '''
    Checks Cloudwatch to ensure event exists, then returns unique amazon resource name (ARN)

    args:
        invoke_source: name of cloudwatch event, as specified in either CLI arg or config file
    '''
    event_name = invoke_source

    if len(event_name)>0:
        try:
            get_events = cloudwatch_client.list_rules(NamePrefix=event_name)
            
            dumper = json.dumps(get_events, indent=4)
            loader = json.loads(dumper)
            if loader['ResponseMetadata']['HTTPStatusCode'] == 200:
                rules = loader['Rules']
                for rule in rules:
                        return rule['Arn']

        except ClientError as error:
            print(error.response['Error']['Message'])

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

def add_invoke_permission(lambda_name, invoke_method=False, invoke_source=False, alias=False, dry_run=False):
    '''
    Creates a policy on the lambda that grants the invoker (sns, s3, cloudwatch) access to invoke
    This must be done before you add the "invoke action" or it will return an error saying you don't have permission

    args:
        lambda_name: name of lambda function, retrieved from config file
        trigger: boolean, used to set up if/else for source & method automatically or to prompt user
        invoke_method: method (sns, cloudwatch, s3), specified by config or CLI arg
        invoke_source: the NAME of the resource, specified by config or CLI arg
        alias: alias you're assigning the trigger to, if you're using one, else defaults to $LATEST
    '''
    if invoke_method:
        invoke_method = invoke_method
        invoke_source = invoke_source
    else:
        invoke_method = input("Enter an invocation method (s3/sns/cloudwatch): ")
        invoke_source = input("Enter an invocation source (bucket name/topic name/event name: ")

    if invoke_method in principals:
        if invoke_method == 's3':
            if check_s3(invoke_source):
                principal = 's3.amazonaws.com'
                print('Using principal: %s' % principal)
                source_arn = 'arn:aws:s3:::%s' % invoke_source
                print('Invoke source arn: %s' % source_arn)
        if invoke_method == 'sns':
            principal = 'sns.amazonaws.com'
            source_arn = get_sns_arn(invoke_source)
        if invoke_method == 'cloudwatch':
            principal = 'events.amazonaws.com'
            source_arn = get_cloudwatch_arn(invoke_source)

        if len(principal)>0:
            if len(source_arn)>0:

                if alias:
                    qualifier = alias
                else:
                    qualifier = ''

                statement_id = "%s-%s-%s" % (lambda_name, alias, invoke_source)        

                if dry_run:
                    print(color.PURPLE + "***Dry Run option enabled***" + color.END)
                    print(color.PURPLE + "Would add permissions for the following:" + color.END)
                    print(color.PURPLE + "Action: 'lambda:InvokeFunction'" + color.END)
                    print(color.PURPLE + "Function Name: %s" % lambda_name + color.END)
                    print(color.PURPLE + "Principal: %s" % principal + color.END)
                    print(color.PURPLE + "SourceArn: %s" % source_arn + color.END)
                    print(color.PURPLE + "StatementId: %s" % statement_id + color.END)
                    print(color.PURPLE + "Qualifier: %s" % qualifier + color.END)
                    return True
                try:
                    add_permission = client.add_permission(
                                                        Action='lambda:InvokeFunction',
                                                        FunctionName=lambda_name,
                                                        Principal=principal,
                                                        SourceArn=source_arn,
                                                        StatementId=statement_id,
                                                        Qualifier=qualifier
                                                    )
                    if add_permission['ResponseMetadata']['HTTPStatusCode'] == 201:
                        print("Invoke permission added for %s" % lambda_name)
                        return True
                    else:
                        return False
                except ClientError as error:
                    print(error.response['Error']['Message'])

def invoke_action(lambda_name, lambda_arn, invoke_method=False, invoke_source=False, alias=False, new_event_type=False, dry_run=False):
    '''
    Adds a subscription/notifier/event to the requested resource (sns, s3, cloudwatch)
    This is the 'important' piece, without this you will only have a policy on the lambda 

    args:
        lambda_name
    '''  
    if alias:
        alias = alias
    else:
        alias = ''

    if invoke_method:
        invoke_method = invoke_method
        invoke_source = invoke_source
    else:
        invoke_method = input("Enter an invocation method (s3/sns/cloudwatch): ")
        invoke_source = input("Enter an invocation source (bucket name/topic name/event name: ")

    if invoke_method == 's3':
        bucket_name = invoke_source
        bucket_notification = s3.BucketNotification(bucket_name)

        if dry_run:
            print(color.PURPLE + "***Dry Run option enabled***" + color.END)
            print(color.PURPLE + "Would add invocation permissions for the following:" + color.END)
            print(color.PURPLE + "Lambda: %s" % lambda_name + color.END)
            print(color.PURPLE + "Bucket: %s" % bucket_name + color.END)
            print(color.PURPLE + "Event: s3:ObjectCreated:*" + color.END)
            return True
        else:
            try:
                e_type = "ObjectCreated"

                if new_event_type:
                    event_type = new_event_type
                else:
                    event_type = e_type

                    if event_type in EVENT_TYPES:
                        e_type = event_type
                    else:
                        print("Event type invalid, removing permissions and rolling back")
                        return False

                put = bucket_notification.put(
                                    NotificationConfiguration={'LambdaFunctionConfigurations': [
                                    {
                                        'LambdaFunctionArn': '%s:%s' % (lambda_arn, alias),
                                        'Events': [
                                                's3:%s:*' % e_type,
                                                ],
                                    }
                                ]
                            }
                        )
                if put['ResponseMetadata']['HTTPStatusCode'] == 200:
                    print("Permssions granted, linked to %s on %s as Lambda invocator" % (invoke_source, invoke_method))
                    return True
            except ClientError as error:
                print(json.dumps(error.response, indent=4))

    if invoke_method == 'sns':
        topic_arn = get_sns_arn(invoke_source)

        if dry_run:
            print(color.PURPLE + "***Dry Run option enabled***" + color.END)
            print(color.PURPLE + "Would add invocation permissions for the following:" + color.END)
            print(color.PURPLE + "TopicArn: %s" % topic_arn + color.END)
            print(color.PURPLE + "Protocol: Lambda" + color.END)
            print(color.PURPLE + "Endpoint: %s" % lambda_arn + color.END)
            return True
        else:
            try:
                subscription = sns_client.subscribe(
                                                TopicArn=topic_arn,
                                                Protocol='Lambda',
                                                Endpoint='%s:%s' % (lambda_arn, alias)
                                            )
                if subscription['ResponseMetadata']['HTTPStatusCode'] == 200:
                    print("Permssions granted, linked to %s on %s as Lambda invocator" % (invoke_source, invoke_method))
                    return True
            except ClientError as Error:
                print(error.response['Error']['Message'])

    if invoke_method == 'cloudwatch':
        rule = invoke_source

        if dry_run:
            print(color.PURPLE + "***Dry Run option enabled***" + color.END)
            print(color.PURPLE + "Would add invocation permissions for the following:" + color.END)
            print(color.PURPLE + "Cloudwatch Rule: %s" % rule + color.END)
            print(color.PURPLE + "ID: %s" % lambda_name + color.END)
            print(color.PURPLE + "Arn: %s" % lambda_arn + color.END)
            return True
        else:
            try:
                add_target = cloudwatch_client.put_targets(
                                            Rule=rule,
                                            Targets=[
                                                {
                                                'Id': lambda_name,
                                                'Arn': '%s:%s' % (lambda_arn, alias),
                                                }
                                            ]
                                        )
                if add_target['ResponseMetadata']['HTTPStatusCode'] == 200:
                    print("Permssions granted, linked to %s on %s as Lambda invocator" % (invoke_source, invoke_method))
                    return True
            except ClientError as error:
                print(error.response['Error']['Message'])

################ Main Actions ##################
def create_trigger(lambda_name, invoke_method, invoke_source, alias, event_type, dry_run):
    '''
    The main entrypoint for the creation action, executes the above functions in the proper order

    args:
        lambda_name: name of lambda, retrieved from config
        invoke_method: sns, s3, cloudwatch, retrieved from config or CLI args
        invoke_source: name of resource, retrieved from config or CLI args
        alias: alias you're assigning the trigger to, retrieved from config or CLI args
        event_type: this is only for s3, but includes all the generic s3 actions 
    '''
    if add_invoke_permission(lambda_name, invoke_method=invoke_method, invoke_source=invoke_source, alias=alias):
        arn = get_lambda_arn(lambda_name)
        
        if invoke_action(lambda_name=lambda_name, lambda_arn=arn, invoke_method=invoke_method, invoke_source=invoke_source, alias=alias, new_event_type=event_type):    
            return True
        else:
            if remove_trigger(lambda_name, alias=alias, invoke_source=invoke_source):
                return False 
    else:
        print("Permissions not granted, see error code")

def remove_trigger(lambda_name, alias=False, invoke_source=False):
    '''
    Removes ability for external resource to trigger the specified lambda

    args:
        lambda_name: name of the lambda, retrived from config file
        trigger: boolean, retrieved from CLI arg
        alias: alias you want to remove the trigger from
        invoke_source: the NAME of the resource you want to drop from being able to invoke
    '''
    if invoke_source:
        invoke_source = invoke_source

    if alias:
        qualifier = alias
    else:
        qualifier = ''

    statement_id = "%s-%s-%s" % (lambda_name, alias, invoke_source)

    try:
        remove = client.remove_permission(
                                FunctionName=lambda_name,
                                StatementId=statement_id,
                                Qualifier=qualifier
                        )
        if remove['ResponseMetadata']['HTTPStatusCode'] == 204:
            print("Successfully removed access permission on %s" % lambda_name)
            return True
    except ClientError as error:
        print(error.response['Error']['Message'])