#External libs
import os
import json
import sys

#Our modules
from maestro.providers.aws.import_lambda import import_lambda

def import_action(lambda_name, alias=False):
	'''
	Calls the import module for AWS provider to collect the configuration
	of the lambda specified in the args. Alias by default is false.

	args:
		lambda_name: the name of the lambda of which we want to import
		alias: the name of the specific alias we want to import
	'''
	#Call the import function
	configuration = import_lambda(lambda_name=lambda_name, alias=alias)

	#Create a file, we'll call it the name of the lambda
	cwd = os.getcwd()
	file = configuration['initializers']['name']
	full_path = os.path.join(cwd, file)

	#Dump the config we retrieved from AWS into the file
	f = open(full_path, 'w')
	f.write(json.dumps(configuration, indent=4))
	f.close()