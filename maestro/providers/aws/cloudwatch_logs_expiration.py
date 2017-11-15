#External libs
import boto3
import sys
import json
import os
from botocore.exceptions import ClientError

#Establish our boto resources
logClient = boto3.client('logs')
lambdaClient = boto3.client('lambda')
iam = boto3.resource('iam')

def invokeFunction(name):
    '''
    Invokes the new function, AWS will generate a log group and stream
    We don't/shouldn't care about the output or if the lambda works, just for the lambda to generate a log group

    args:
        name: name of the lambda, retrieved from config file
    '''
    print('Creating log group')
    try:
        invoke = lambdaClient.invoke(FunctionName=name)
    except ClientError as error:
        print(error)

def getLogGroupName(name):
    '''
    Gets the unique amazon resource name (ARN) for the log group we are creating with 'invokeFunction'
    Accomplishes this by searching existing log groups for the name of the function

    Note: All Lambda generated log groups are prefixed with '/aws/lambda', as seen below
    
    args:
        name: the name of the lambda function, retried from config file
    '''
    print('Getting lambda log group name')
    try:
        logGroupName = logClient.describe_log_groups(
                logGroupNamePrefix='/aws/lambda/%s' % name,
            )

        dump = json.dumps(logGroupName, indent=4)
        load = json.loads(dump)

        if logGroupName['ResponseMetadata']['HTTPStatusCode'] == 200:
            groupName = load['logGroups'][0]['logGroupName']
            groupArn = load['logGroups'][0]['arn']

            print('Group name: %s' % groupName)
            return groupName, groupArn
    except ClientError as error:
        print(error)

def putRetentionPolicy(log_group_name, retention_time):
	'''
	Puts a retention poliy on the log group for the specified lambda

	args:
		log_group_name: name of the cloudwatch log group for the lambda (retrieved from getLogGroupName)
		retention_time: integer, in days, of how long we want to keep logs around
	'''
	print('Attempting to put a retention policy of %s days on %s' % (retention_time, log_group_name))
	try:
		put_policy = logClient.put_retention_policy(
							logGroupName=log_group_name,
							retentionInDays=retention_time
						)
	except ClientError as error:
		print(error.response)
		sys.exit(1)

########## Main Entrypoint ############
def set_cloudwatch_log_expiration(name, retention_time):
	'''
	the main entrypoint for the log expiration module, calls all above functions to simplify the interface
	
	args:
		name: name of the lambda we're setting up logging for 
		retention_time: integer, in days, that we retrieve from the config file
	'''
	invoke = invokeFunction(name)
	groupName, _ = getLogGroupName(name)
	put_policy = putRetentionPolicy(groupName, retention_time)
