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

ARGS = parser.parse_args()
