import argparse
import sys

parser = argparse.ArgumentParser(
	prog='maestro',
	description='Manage AWS Lambdas from the command line'
	)
parser.add_argument(
	'action', 
	choices=['init', 'import', 'create', 'update-code', 'update-config','delete', 'publish', 'create-alias', 'delete-alias', 'update-alias', 'invoke'],
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
	action='store_true',
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
	'--invoke_type',
	help="Choose from Event, RequestResponse, or Dry Run")
parser.add_argument(
	'--payload',
	help='Input a filename for your test payload')
parser.add_argument(
	'--no_pub',
	action='store_true',
	help='Deploys code to $LATEST')
parser.add_argument(
	'--version',
	help='Select a version to invoke')
parser.add_argument(
	'--event_type',
	help="Indicate event type for S3 only. You can choose 'created' or 'deleted'")
parser.add_argument(
	'--version_description',
	help="Pass a description into the version")
parser.add_argument(
	'--weight',
	help="Percentage of traffic getting sent to newest published version")
parser.add_argument(
	'--var', nargs=2, action='append')
ARGS = parser.parse_args()