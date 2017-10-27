import json
import boto3
from botocore.exceptions import ClientError

logClient = boto3.client('logs')
lambdaClient = boto3.client('lambda')
iam = boto3.resource('iam')

#Invoke the function, creating the log group
def invokeFunction(name):
	print('Creating log group')
	try:
		invoke = lambdaClient.invoke(FunctionName=name)
	except ClientError as error:
		print(error)

#Get the group name of the new lambda, this is more of a check to see if it exists
def getLogGroupName(name):
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

#Get the arn of the logging lambda
def getDestinationArn(destLambda, destAlias):
	print('Getting destination arn for logging lambda')
	try:
		destinationArn = lambdaClient.get_function(
							FunctionName=destLambda,
							Qualifier=destAlias
						)

		dump = json.dumps(destinationArn, indent=4)
		load = json.loads(dump)

		arn = load['Configuration']['FunctionArn']

		return arn
	except ClientError as error:
		print(error)

#Add subscription filter to new lambda to pipe logs to logging lambda
def putSubfilter(groupName, arn, role, name):
	print('Adding subscription filter to logging lambda')
	try:
		putFilter = logClient.put_subscription_filter(
						logGroupName=groupName,
						filterName='LambdaLogging_%s' % name,
						filterPattern='',
						destinationArn=arn,
					)
	except ClientError as error:
		print(error)

#Add the ability for the new lambda logs to invoke the logging lambda
def putInvokePerm(destLambda, destAlias, name, region, logArn):
	print('Adding invoke permission to logging lambda')
	try:
		addPermission = lambdaClient.add_permission(
							FunctionName=destLambda,
							Action='lambda:InvokeFunction',
							StatementId='%s-log-invoke-%s' % (name, destAlias),
							Principal='logs.%s.amazonaws.com' % region,
							Qualifier=destAlias,
							SourceArn=logArn
						)
	except ClientError as error:
		print(error)

#Get role arn
def getRoleArn(role):
	print('Gathering role arn')
	try:
		role = iam.Role('name')

		return role.arn
	except ClientError as error:
		print(error)

########## Main Entrypoint ############
def cloudwatchSubscription(newLambdaName, destLambdaName, destLambdaAlias, region, role):
	invocation = invokeFunction(newLambdaName)
	groupName, groupArn = getLogGroupName(newLambdaName)
	arn = getDestinationArn(destLambdaName, destLambdaAlias)
	roleArn = getRoleArn(role)
	permission = putInvokePerm(destLambdaName, destLambdaAlias, newLambdaName, region, groupArn)
	subscription = putSubfilter(groupName, arn, roleArn, newLambdaName)
