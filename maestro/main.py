#External Libs
import json
import os
import sys

#Get CLI Args
from maestro.cli import ARGS

#Alias module
from maestro.alias import alias_creation as alias_creation
from maestro.alias import alias_destroy as alias_destroy
from maestro.alias import alias_update as alias_update

#Trigger module
from maestro.triggers import create_trigger as create_trigger
from maestro.triggers import remove_invoke_action as delete_trigger

#DLQ module
from maestro.dlq import get_sns_arn
from maestro.dlq import get_sqs_arn

#Core actions
from maestro.create_lambda import create
from maestro.publish_lambda import publish
from maestro.delete_lambda import delete
from maestro.update_lambda_code import update_code
from maestro.update_lambda_config import update_config

#Everything else
from maestro.security_groups import security_groups as security_groups_method
from maestro.s3_backup import main as s3_backup
from maestro.invoke import main as invoke
from maestro.cloudwatch_sub import cloudwatchSubscription
from maestro.config_validator import validation
from maestro.zip_function import zip_function
from maestro.check_existence import check
from maestro.role_arn import get_arn
import maestro.vpc_location as vpc_location
import maestro.lambda_config as lambda_config

## This will serve as the point that calls all actions, it will replace the massive and ugly current main function
def main():
	pass