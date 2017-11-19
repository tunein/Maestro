# Maestro documentation

---

## A note about roles

The Maestro user should have access to the following resources:

- Lambda  
- IAM
- S3  
- SNS 
- SQS  
- Cloudwatch   
- DynamoDB     
- Kinesis   

The choice to use "full access" or customized IAM policies is up to you.  

*If you're using Maestro in a CICD pipeline it is recommended to create a maestro IAM user.*    
*If you're deploying from your local machine the same necessary permissions are needed.*  

---
Config file template
```
{
 "initializers": { \\ required
    "name": "string", \\ the name of your lambda
    "description": "string", \\ a description of your lambda
    "region": "string", \\ valid aws region
    "role": "string", \\ a valid IAM role
    "handler": "example.main", \\ the handler of your lambda
    "alias": "string", \\ used for creating an alias or updating your code/config using a specific alias -- optional
    "tracing_mode": "string" \\ trace mode, disabled by default (if not in config file) options: active -- optional
  },
 "provisioners": { \\ required
    "runtime": "string", \\ a valid runtime
    "timeout": int, \\ length (in seconds) between 1-300 seconds
    "mem_size": int, \\ size (in mb), must be greater than 128mb and divisble by 64 (see allowed sized below)
 },
 "vpc_setting": { \\ optional  
    "vpc_name": "example-vpc", \\ the NAME of your vpc, see details below 
    "security_group_ids": ["example-sg"] \\ the NAME of the security groups you'd like to assign 
 },
 "variables": { \\ optional 
    "key": "value" \\ variables, these can be as few as 1 and as many as AWS allows 
 },
 "dead_letter_config": { \\ optional
    "type": "sns/sqs", \\ choice of sns or sqs
    "target_name": "string" \\ the NAME of your sns topic or sqs queue
 },
  "tags": { \\ optional
    "key": "value" \\ tags for your lambda, there can be as few as 1 and as many as AWS allows
 },
 "logging": { \\ optional
    "destination_lambda": "string", \\ name of a log processing lambda, subscribes lambda cloudwatch logs to it 
    "destination_alias": "string" \\ alias, if applicable of the log processing lambda
 },
 "log_expiration": { \\ optional
    "age": int \\ age, in days, that you'd like your logs to live before expiration. see below for valid amounts
 },
 "trigger": { \\ optional
    "method": "s3/sns/cloudwatch", \\ choice of s3/sns/cloudwatch (events)
    "source": "string" \\ the NAME of your source (s3 bucket, sns topic, cloudwatch event)
    "event_type": "string" \\ s3 only, the type of event (ObjectCreated, ObjectDeleted, etc. See AWS docs)
 },
 "event_stream": { \\ optional 
    "type": "kinesis/dynamodb", \\ choice of kinesis or dynamodb
    "source": "string", \\ the NAME of the dynamodb or kinesis stream
    "batch_size": int, \\ an integer for how large you want the batch size to be
    "enabled": "True/False", \\ True or False, you must use double quotes
    "start_position": "TRIM_HORIZON/LATEST/AT_TIMESTAMP" \\ your choice of TRIM_HORIZON/LATEST/AT_TIMESTAMP, caps count
 },
 "backup": { \\ optional
    "bucket_name": "string" \\ The name of an s3 bucket you want to back up your ZIP'd lambda code to
 }
}
```
---

## The initializers section  

The initializers section is where you put the basics of your lambda. This is required.

Required fields are:  
- name  
- description  
- region  
- role  
- handler  

Optional fields are:  
- alias  
- tracing mode  

Remember! Capitalization counts!

---

## How to use an 'alias' in initializers in the config file

The alias field in 'initializers' is used to either create an alias (if it doesn't exist) or the 'update-alias' action  

This is extremely useful in the following ways:  
- Allows you to use `update-code` with the `--no-publish` flag to upload your new code to $LATEST, then run tests before promoting the new code to your active alias (where your trigger/event stream is activing the current production code)
- Prevents you from having to identify `--alias` when running commands, keeps your commands short and to the point

--- 

## Provisioners section

This is where you set up the runtime, timeout, and memory size of your lambda

Fields:  

runtime:    
- nodejs4.3  
- nodejs6.10  
- java8  
- python2.7  
- python3.6  
- dotnetcore1.0  
- nodejs4.3-edge  

timeout:
- An integer between 1 and 300 seconds

mem_size:

The minimum memory size of a Lambda is 128mb. It scales up from there, in divisbles of 64, up to 1536mb  

It is up to you, and your code, how much memory you will need.

---

## How to use 'vpc_setting' in the confile file

Fields:

vpc_name:
- The expectation of Maestro is that your VPC has name, anything will do, use this name for the "vpc_name" field  
- The expection of Maestro is that your VPC's subnets have ONE TAG and ONE TAG ONLY. 
- The naming convention of those tags is {"Name": "subnet-name-public/private"}
- Maestro finds the "private" subnets and attaches the lambda to those subnets (the name just needs private in it)

security_group_ids:
- These are the actual names of your security groups, not the sg-id assigned by amazon
- If you are using a lambda in a VPC it is a requirement of Maestro you use at least one security group

---

## How to use 'logging' in the config file  

This setting is used to set up a Cloudwatch Log subscription.  
At the time of this writing the supported log subscription is to other Lambdas only.  

Fields:  

destination_lambda:  
- The NAME of your logging lambda  

destination_alias:  
- The ALIAS of your logging lambda, if no alias is found it defaults to $LATEST  

---

## How to use 'log_expiration' in the config file  

This setting in the config file signifies the amount of days you want your Cloudwatch logs to live before expiration   

Possible options:
```1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653```  

---

## How to use 'variables' in the config file

This is a standard key, value dictionary. If you include it you must have at least 1 key/value.

This section is optional

---

## How to use 'tags' in the config file  

This is a standard key, value dictionary. If you include it you must have at least 1 key/value.  

This section is optional  

---

## How to use 'dead_letter_config' in the config file  

The dead letter config field allows you to set up a dead letter queue for your Lambda  

Fields:  

type:
- Your choice of sqs or sns

target_name:
- The NAME of your sqs queue or sns topic

---

## How to use 'trigger' in the config file

The triggers field allows you to set up your Lambda triggers automatically. When used it not only handles placing a valid policy on the lambda but also adds the necessary subscriptions/events on the s3 bucket/sns topic/cloudwatch event.  

If used in conjunction with the 'alias' field in the 'initializers' dictionary it automatically assigns the trigger to the specified alias.  

Fields:  

method:  
- Choice of s3, sns, or cloudwatch (note: cloudwatch is used for Cloudwatch Events)

source:  
- The NAME of your s3 bucket, sns topic, or cloudwatch event

event_type:  
- This is valid only for the s3 method, see AWS docs for valid s3 event notifier types

---

## How to use 'event_stream' in the config file

The event stream field is used to set up an event stream trigger via DynamoDB or Kinesis streams. When used this handles all necessary subscriptions and permissions. 

If used in conjunction with the 'alias' field in the 'initializers' dictionary it automatically assigns the trigger to the specified alias.  

Fields: 

type:  
- Choice of kinesis or dynamodb  

source:  
- The NAME of your kinesis stream or dynamodb stream  

batch_size:  
- An integer, the size of the batch you want to process  

enabled:  
- "True" of "False", you must use double quotes  

start_position:  
- Choice of TRIM_HORIZON, LATEST, or AT_TIMESTAMP, read AWS docs if you are not familiar  

---

## How to use 'backup' in the config file  

This field is used to specify an S3 bucket that you're backing up your ZIP'd code to after a deployment.

Fields:

bucket_name:  
- The name of a valid S3 bucket, if it doesn't exist Maestro will ask if you want to create it.
