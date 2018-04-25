#External libs
import boto3
import json
import os
import sys
import datetime
from botocore.exceptions import ClientError

#Establish our boto resources
dynamoStreamClient = boto3.client('dynamodbstreams')
lambdaClient = boto3.client('lambda')
kinesisClient = boto3.client('kinesis')

def datetime_handler(x):
    '''
    Helper function for parsing datetime in json responses
    '''
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

def get_lambda_arn(lambda_name=None, alias=False):
    '''
    Retrieves unique amazon resource name (ARN) of lambda, for usage in the 'invoke_action' function

    args:
        lambda_name: the name of the lambda, retrieved from the config file
    '''
    try:
        repsonse = lambdaClient.get_function(FunctionName=lambda_name)

        arn = repsonse['Configuration']['FunctionArn']

        if alias:
            arn = arn + ":%s" % alias
        else:
            arn = arn 

        return arn
    except ClientError as error:
        print(color.RED + error.response['Error']['Message'] + color.END)

def get_dynamo_stream(table):
    '''
    Gets the arn of a dynamodb table

    args:
        table: the name of a valid dynamodb table
    '''
    try:
        table_streams = dynamoStreamClient.list_streams(TableName=table)

        if table_streams['ResponseMetadata']['HTTPStatusCode'] == 200:
            stream_arn = table_streams['Streams'][0]['StreamArn']

            print("Found valid DynamoDB Stream: " + stream_arn)

            return stream_arn
    except ClientError as error:
        print(error.response)

def get_kinesis_stream(stream):
    '''
    Gets the arn of a kenesis stream

    args:
        stream: the name of a kenesis stream
    '''
    try:
        get_stream = kinesisClient.describe_stream(StreamName=stream)

        if get_stream['ResponseMetadata']['HTTPStatusCode'] == 200:
            stream_arn = get_stream['StreamDescription']['StreamARN']

            print("Found valid kinesis Stream: " + stream_arn)

            return stream_arn
    except ClientError as error:
        print(error.response)

def create_event_source_trigger(lambda_arn=None, event_source=None, enabled=False, batch_size=False, starting_position=False):
    '''
    Creates event source mapping for lambda -> dynamodb/kinesis

    args:
        lambda_name: name of the lambda
        event_source: the amazon resource name (ARN) of the source (kenesis or dynamodb)
        enabled: Boolean, false by default
        batch_size: integer
        starting_position: Choice of 'TRIM_HORIZON', 'LATEST', 'AT_TIMESTAMP'
    '''
    try:
        lambda_event_source = lambdaClient.create_event_source_mapping(
                            EventSourceArn=event_source, 
                            FunctionName=lambda_arn, 
                            Enabled=enabled, 
                            BatchSize=batch_size, 
                            StartingPosition=starting_position
                            )
        
        if lambda_event_source['ResponseMetadata']['HTTPStatusCode'] == 202:
            print("Creating event source mapping")
            return True
    except ClientError as error:
        print(error.response)

def list_event_sources(source_arn, lambda_arn):
    '''
    Gets the UUID of the current event source so we can update it
    
    args:
        source_arn: the arn of the kinesis or dynamodb stream, retrieved from get arn helper functions
        lambda_name: name of the lambda, retried from config file
    '''
    try:
        current_sources = lambdaClient.list_event_source_mappings(FunctionName=lambda_arn, EventSourceArn=source_arn)

        if current_sources['ResponseMetadata']['HTTPStatusCode'] == 200:
            if len(current_sources['EventSourceMappings']) > 0:

                uuid = current_sources['EventSourceMappings'][0]['UUID']
                batch_size = current_sources['EventSourceMappings'][0]['BatchSize']
                state = current_sources['EventSourceMappings'][0]['State']
                source = current_sources['EventSourceMappings'][0]['EventSourceArn']

                if state == 'Enabled':
                    state = True
                else:
                    state = False
                    
                return uuid, batch_size, state, source
            else:
                return False
    except ClientError as error:
        print(error.response)

def update_event_source_trigger(uuid=None, lambda_arn=None, enabled=False, batch_size=None):
    '''
    updates current event source

    args:
        uuid: the uuid of the current event source
        lambda_name: name of the lambda we're working with
        enabled: Boolean, false by default
        batch_size: size of records being processed
    '''
    print('Attempting to update current event source')
    try:
        update_event = lambdaClient.update_event_source_mapping(
                                            UUID=uuid,
                                            FunctionName=lambda_arn,
                                            Enabled=enabled,
                                            BatchSize=batch_size
                                        )

        if update_event['ResponseMetadata']['HTTPStatusCode'] == 202:
            print("Event source updated!")
            return True
    except ClientError as error:
        print(error.response)

############## Main Entry Point ##############
def create_event_source(source_type=None, source_name=None, lambda_name=None, batch_size=None, enabled=False, starting_position=False, alias=False):
    '''
    Entrypoint for adding an event source as the lambda invocator 

    args:
        source_type: kinesis or dynamodb
        source_name: the name of the resource 
        lambda_name: name of the lambda we're going to be triggering
        enabled: boolean, False by default
        starting_position: Choice of 'TRIM_HORIZON', 'LATEST', 'AT_TIMESTAMP'
    '''

    #Get the source type and assign the value of stream accordingly 
    if source_type == 'kinesis':
        stream = get_kinesis_stream(source_name)
    elif source_type == 'dynamodb':
        stream = get_dynamo_stream(source_name)
    else:
        print("No valid source type found, please use 'kinesis', or 'dynamodb'")
        sys.exit(1)

    #Get lambda arn, this is for aliases
    arn = get_lambda_arn(lambda_name=lambda_name, alias=alias)

    #Create the mapping
    create = create_event_source_trigger(lambda_arn=arn, event_source=stream, enabled=enabled, batch_size=batch_size, starting_position=starting_position)

    if create:
        print("Event source created successfully")
        return True

def update_event_source(source_type=None, source_name=None, lambda_name=None, batch_size=None, enabled=False, alias=False):
    '''
    Main entry point for updating the event source. The first thing it does is get the arn for the desired resource
    then it checks to see if we actually need an update by validating our current state against our desired state.
    If the match it exits gracefully, else it will perform an update

    args:
        source_type: kinesis or dynamodb
        source_name: name of the resource (table name or stream name)
        lambda_name: name of the lambda function
        batch_size: integer, size of batch per lambda invocation
        enabled: Boolean, false by default
    '''
    if source_type == 'kinesis':
        stream = get_kinesis_stream(source_name)
    elif source_type == 'dynamodb':
        stream = get_dynamo_stream(source_name)
    else:
        print("No valid source type found, please use 'kinesis', or 'dynamodb'")
        sys.exit(1)

    #Get lambda arn, this is for aliases
    arn = get_lambda_arn(lambda_name=lambda_name, alias=alias)
    
    #Get all of our current values
    current_uuid, current_batch_size, current_state, current_source = list_event_sources(source_arn=stream, lambda_arn=arn)

    #Validates what we want vs what we have
    if all(item in [stream, batch_size, enabled] for item in [current_source, current_batch_size, current_state]):
        print('No update needed')
        return True
    else:
        print('Updating event source')
        update = update_event_source_trigger(uuid=current_uuid, lambda_arn=arn, enabled=enabled, batch_size=batch_size)

def check_source_mapping(source_type=None, source_name=None, lambda_name=None, alias=False):
    '''
    Gets current event source config and reports back to update-config action. This is used to see if we need to either update
    or create the event source mapping

    args:
        source_type: kinesis or dynamodb
        source_name: name of the resource (table name or stream name)
        lambda_name: name of the lambda function
    '''
    if source_type == 'kinesis':
        stream = get_kinesis_stream(source_name)
    elif source_type == 'dynamodb':
        stream = get_dynamo_stream(source_name)
    else:
        print("No valid source type found, please use 'kinesis', or 'dynamodb'")
        sys.exit(1)

    #Get arn
    arn = get_lambda_arn(lambda_name=lambda_name, alias=alias)
    
    #Get our current sources
    get_sources = list_event_sources(source_arn=stream, lambda_arn=arn)

    #If get sources returns true it means the mapping is there and we only need to update, else we'll need to create
    if get_sources:
        return True
    else:
        return False