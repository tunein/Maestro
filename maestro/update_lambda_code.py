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