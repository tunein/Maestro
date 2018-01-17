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
        print('Checking function concurrency setting')
        try:
            putConcurrency = client.put_function_concurrency(
                                FunctionName=functionName,
                                ReservedConcurrentExecutions=reservedCapacity
                            )
        except ClientError as error:
            print(error)
            sys.exit(1)
        finally:
            print('Function concurrency limit updated')
            return True
    else:
        raise RuntimeError('Must supply a valid function name')