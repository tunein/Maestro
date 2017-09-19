import argparse
import sys

parser = argparse.ArgumentParser(
	prog='maestro',
	description='Manage AWS Lambdas from the command line'
	)
parser.add_argument(
	'action', 
	choices=['create', 'update-code', 'update-config','delete', 'publish', 'create-alias', 'delete-alias', 'update-alias'],
	help='Pick from one of the actions to start'
	)
parser.add_argument(
	'filename',
	help='Input a json file'
	)
parser.add_argument(
	'--create_trigger',
	action='store_true',
	help='Creates a lambda trigger. If added you must provide invoke method and invoke source'
	)
parser.add_argument(
	'--delete_trigger',
	help='Deletes a lambda trigger'
	)
parser.add_argument(
	'--invoke_method',
	choices=['s3', 'sqs', 'sns', 'cloudwatch'],
	help='Pick from available invoke methods',
	)
parser.add_argument(
	'--invoke_source',
	help="The name of the resource you'd like to trigger your lambda with",
	)
parser.add_argument(
	'--alias',
	help="Give your alias a name (ie: dev, stage, prod)")
parser.add_argument(
	'--publish',
	action='store_true',
	help="Used only for update-code, true or false")
parser.add_argument(
	'--dry_run',
	action='store_true',
	help="Performs all actions as a dry run")
parser.add_argument(
	'--invoke',
	action='store_true',
	help="Invokes your lambda")
ARGS = parser.parse_args()
