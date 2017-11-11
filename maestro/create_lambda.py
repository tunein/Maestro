#External libs
import boto3
import sys
import json
import os
from botocore.exceptions import ClientError

#Our modules
import maestro.lambda_config as lambda_config
from maestro.role_arn import get_arn
from maestro.vpc_location import main as vpc_location
from maestro.security_groups import security_groups
from maestro.dlq import get_sns_arn
from maestro.dlq import get_sqs_arn
from maestro.zip_function import zip_function

#Establish our boto resources
client = boto3.client('lambda')

#Establish easy to read variables for stuff from config file
TRACING_TYPES = lambda_config.TRACE_TYPES

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

def create(lambda_name, runtime, role, handler, description, timeout, mem_size, vpc_setting=False, config_vpc_name=False, 
			config_security_groups=False, tags=False, publish=False, variables=False, dead_letter_config=False, dlq_type=False, 
			dlq_name=False, tracing_mode=False, dry_run=False):
	'''
	The main create function, this handles the creation of lambdas

	args:
		lambda_name: name of the lambda, retrieved from config file
		runtime: runtime (python, node, .NET ect) of the lambda, retrieved from config
		role: valid AWS role, retrieved from config
		handler: the main entrypoint of your code, module.function_name
		description: simple description of the lambda
		timeout: integer in seconds for long the lambda runs
		mem_size: integer in mb for how much memory your lambda needs
		vpc_setting: boolean, if yes grab vpc name and security group ids from config
		config_vpc_name: vpc name from config file
		config_security_groups: security group names from config file
		tags: a dictionary of tags copied from config file
		publish: boolean, if true publishes a version of the lambda
		variables: dictionary of environment variables for the lambda, grabbed from config file
		dead_letter_config: boolean, if yes grab dlq type and name from config
		dlq_type: dlq type from config file (sns or sqs)
		dlq_name: dlq name from the config file
		tracing_mode: active or not, grabbed from config file
		dry_run: CLI arg for if the user wants to just see what would happen
	'''
	archive_name = os.getcwd() + '/%s.zip' % lambda_name

	subnet_ids = []
	security_group_id_list = []

	if vpc_setting:
		#write subnets IDs to an array for later
		subnets = vpc_location(config_vpc_name)
		subnet_ids.extend(subnets)

		#write security group IDs to an array for later
		groups = security_groups(config_security_groups)
		security_group_id_list.extend(groups)
	else:
		pass

	tags = {}

	#Copy the tags dictionary from the config file
	if tags:
		tags.update(tags)
	else:
		pass

	if len(subnet_ids)>0:
		vpc_config = {
						'SubnetIds': subnet_ids,
						'SecurityGroupIds': security_group_id_list
					}
	else:
		vpc_config = { }

	#Check for publish CLI flags
	if publish:
		pub = True
	else:
		pub = False

	#Grab variables, if they exist
	if variables:
		env_vars = variables
	else:
		env_vars = { }

	#DLQ configuration, write the necessary info to the target arn dictionary
	target_arn = { }

	if dead_letter_config:
		dlq_type = dlq_type
		dlq_name = dlq_name
		if dlq_type == 'sns':
			arn = get_sns_arn(dlq_name)
			target_arn.update({'TargetArn': arn})
		elif dlq_type == 'sqs':
			arn = get_sqs_arn(dlq_name)
			target_arn.update({'TargetArn': arn})
		else:
			raise RuntimeError('No valid DLQ type found')
	else:
		pass

	#Write the tracing config to the trace_type dictionary
	trace_type = { }

	if tracing_mode:
		mode = tracing_mode
		if mode in TRACING_TYPES:
			if mode == "active":
				capmode = "Active"
				trace_type.update({'Mode': capmode})
			elif mode == "passthrough":
				capmode = "PassThrough"
				trace_type.update({'Mode': capmode})
		else:
			raise RuntimeError('No valid trace mode found')
	else:
		trace_type = {'Mode': 'PassThrough'}

	#Zip the function into a deployable package
	if zip_function(lambda_name):
		if dry_run:
			print(color.BOLD + "***Dry Run option enabled***" + color.END)
			print(color.PURPLE + "Would have attempted to create the following:" + color.END)
			print(color.PURPLE + "FunctionName: %s" % lambda_name + color.END)
			print(color.PURPLE + "Runtime: %s" % runtime + color.END)
			print(color.PURPLE + "Role: %s" % role + color.END)
			print(color.PURPLE + "Handler: %s" % handler + color.END)
			print(color.PURPLE + "Archive: %s" % archive_name + color.END)
			print(color.PURPLE + "Description: %s" % description + color.END)
			print(color.PURPLE + "Timeout: %s" % timeout + color.END)
			print(color.PURPLE + "Memory Size: %s" % mem_size + color.END)
			print(color.PURPLE + "VPC Config: %s" % vpc_config + color.END)
			print(color.PURPLE + "Environment Variables: %s" % env_vars + color.END)
			print(color.PURPLE + "DLQ Target: %s" % target_arn)
			print(color.PURPLE + "Tracing Config: %s" % trace_type)
			print(color.PURPLE + "Tags: %s" % tags)
			return True
		else:
			print(color.CYAN + "Attempting to create lambda..." + color.END)
			try:
				create = client.create_function(
					FunctionName=lambda_name,
					Runtime=runtime,
					Role='%s' % get_arn(role),
					Handler=handler,
					Code={
						'ZipFile': open(archive_name, 'rb').read()
					},
					Description=description,
					Timeout=timeout,
					MemorySize=mem_size,
					Publish=pub,
					VpcConfig=vpc_config,
					Environment={
						'Variables': env_vars
						},
					DeadLetterConfig=target_arn,
					TracingConfig=trace_type,
					Tags=tags
				)
				if create['ResponseMetadata']['HTTPStatusCode'] == 201:
					return True
				else:
					return False
			except ClientError as error:
				print(color.RED + error.response['Error']['Message'] + color.END)
				sys.exit(1)