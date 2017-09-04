import boto3
import lambda_config
import sys
import json
import os
import datetime
from botocore.exceptions import ClientError
DOC = sys.argv[2]

def json_parser():
  with open('%s' % DOC) as json_data:
    read = json.load(json_data)
    return read
    return True
  print("No json document to read.. Please enter a valid json document")