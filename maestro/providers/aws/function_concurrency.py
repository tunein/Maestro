#External libs
import boto3
import json
import os
import sys
from botocore.exceptions import ClientError

#Establish our boto resources
client = boto3.client('lambda')

def putFunctionConcurrency(functionName=None, reservedCapacity=100):
    pass

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
        print('Must supply function name')
        sys.exit(1)