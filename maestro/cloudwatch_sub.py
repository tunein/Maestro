#External libs
import json
import boto3
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

def getDestinationArn(destLambda, destAlias):
    '''
    Retrieves the unique amazon resource name (ARN) for the destination lambda
    This unique id is required to accomplish the function below (putSubFilter)
    We need the alias because each alias has it's own arn (if you're using one)

    args:
        destLambda: name of the processing lambda
        destAlias: name of the alias on the processing lambda
    '''
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

def putSubfilter(groupName, arn, role, name):
    '''
    Adds subscription filter to new lambda to pipe logs to logging lambda

    Takes info from 'getLogGroupName', 'getDestinationArn', then the role and new lambda name from the config file

    args:
        groupName: name retrieved by 'getLogGroupName'
        arn: the amazon resource name (ARN) for the destination lambda
        role: not sure why this is still here, i probably forgot to remove it, likely removeable?
        name: the name of the new lambda, from the config file, used to create a unique filterName for the sub filter
    '''
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

def putInvokePerm(destLambda, destAlias, name, region, logArn):
    '''
    Adds the ability for the new lambda logs to invoke the logging lambda
    This can be seen in the triggers of the destination lambda

    args:
        destLambda: name of the destination lambda, retrieved from config
        destAlias: alias on the destination lambda, retrieved from config
        name: name of the new lambda, retrieved from config, used to create a statement id
        region: region this is happening in, used for the principal, seen below
        logArn: arn of the new lambda log group, retried from 'getLogGroupName'
    '''
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

def getRoleArn(role):
    '''
    Get unique amazon resource name (ARN) of the role, this is used in 'putInvokePerm' function

    args:
        role: name of the role you're using, retrieved from config
    '''
    print('Gathering role arn')
    try:
        role = iam.Role('name')

        return role.arn
    except ClientError as error:
        print(error)

########## Main Entrypoint ############
def cloudwatchSubscription(newLambdaName, destLambdaName, destLambdaAlias, region, role):
    '''
    To simplify usage of this module This is the main entrypoint that calls all above modules

    I've debated putting the above in a class but it seems like overkill to accomplish what is already working

    args:
        new_lambda_name: name the lambda we're creating, retrieved from config file
        dest_lambda_name: name of lambda processing our logs, retrieved from config file
        dest_lambda_alias: name of the ALIAS of the lambda processing our logs, retrieved from config file
        region: region this will occur in, retried from config file
        role: a valid role that can execute the necessary actions involved with this module (ie: invoke, put permissions)
    '''
    invocation = invokeFunction(newLambdaName)
    groupName, groupArn = getLogGroupName(newLambdaName)
    arn = getDestinationArn(destLambdaName, destLambdaAlias)
    roleArn = getRoleArn(role)
    permission = putInvokePerm(destLambdaName, destLambdaAlias, newLambdaName, region, groupArn)
    subscription = putSubfilter(groupName, arn, roleArn, newLambdaName)
