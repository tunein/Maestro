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
ARGS = parser.parse_args()
