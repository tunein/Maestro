#External libs
import boto3
import json
import os
import sys
from botocore.exceptions import ClientError

#Establish our boto resources
client = boto3.client('lambda')

def putFunctionConcurrency(functionName=None, reservedCapacity=100):
    if functionName is not None:
        try:
            putConcurrency = client.put_function_concurrency(
                                FunctionName=functionName,
                                ReservedConcurrentExecutions=reservedCapacity
                            )
        except ClientError as error:
            print(error)
            sys.exit(1)
        finally:
            if putConcurrency['ResponseMetadata']['HTTPStatusCode'] == 201:
                return True
    else:
        raise RuntimeError('Must supply a valid function name')

def removeFunctionConcurrency(functionName=None):
    if functionName is not None:
        try:
            print('Attempting to remove function concurrency')
            remove = client.delete_function_concurrency(FunctionName=functionName)
        except ClientError as error:
            print(error)
            sys.exit(1)
        finally:
            return True
    else:
        raise RuntimeError('Must supply a valid function name')