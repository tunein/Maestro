import argparse
import sys


parser = argparse.ArgumentParser(
	prog='maestro',
	description='Manage AWS Lambdas from the command line')

parser.add_argument(
	'action', 
	choices=['create', 'update-code', 'update-config','delete', 'publish', 'create-alias', 'delete-alias', 'update-alias'],
	help='Pick from one of the actions to start'
	)
parser.add_argument(
	)

args = parser.parse_args()

'''
this is a different approach for a more robust CLI. I'll finish it soon.

## Main action
main_actions = argparse.ArgumentParser(
			prog='maestro',
			description='Manage AWS Lambdas from the command line')

main_actions.add_argument(
	'create', nargs='+')
main_actions.add_argument(
	'update', nargs='+')
main_actions.add_argument(
	'delete', nargs='+')
main_actions.add_argument(
	'publish', nargs='+')

## Sub actions
sub_actions = argparse.ArgumentParser(
			parents=[main_actions])

parser.add_argument(
	'alias', )
parser.add_argument(
	'code', )
parser.add_argument(
	'config', )
'''
