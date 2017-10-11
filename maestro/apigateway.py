import boto3
import sys
import os
import json
import datetime
from botocore.exceptions import ClientError

client = boto3.client('apigateway')


# service = apigateway.amazonaws.com

def datetime_handler(x):
  if isinstance(x, datetime.datetime):
      return x.isoformat()
  raise TypeError("Unknown type")

def get_apis():
	response = client.get_rest_apis()
	dump = json.dumps(response, default=datetime_handler, indent=4)
	load = json.loads(dump)

	name = "PetStore"

	api_id = ""

	for item in load['items']:
		if name in item['name']:
			api_id = item['id']
		else:
			pass

	if len(api_id)>0:
		try:
			get_resource = client.get_resources(restApiId=api_id)
			print(json.dumps(get_resource, default=datetime_handler, indent=4))
		except ClientError as error:
			print(error)

get_apis()