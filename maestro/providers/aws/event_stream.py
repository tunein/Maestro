#External libs
import boto3
import json
import os
import sys
import datetime
from botocore.exceptions import ClientError

dynamoStreamClient = boto3.client('dynamodbstreams')
lambdaClient = boto3.client('lambda')
kinesisClient = boto3.client('kinesis')

def datetime_handler(x):
        if isinstance(x, datetime.datetime):
            return x.isoformat()
        raise TypeError("Unknown type")

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

def create_event_source_trigger(lambda_name=None, event_source=None, enabled=False, batch_size=False, starting_position=False):
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
                            FunctionName=lambda_name, 
                            Enabled=enabled, 
                            BatchSize=batch_size, 
                            StartingPosition=starting_position
                            )
        
        if lambda_event_source['ResponseMetadata']['HTTPStatusCode'] == 202:
            print("Creating event source mapping")
            return True
    except ClientError as error:
        print(error.response)

#stream = get_dynamo_stream('maestro-test-table')
stream = get_kinesis_stream('maestro-test-stream')
create = create_event_source_trigger(lambda_name='trigger-test', event_source=stream, enabled=True, batch_size=100, starting_position='TRIM_HORIZON')