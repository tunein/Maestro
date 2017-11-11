#External Libs
import json
import os
import sys

#Get CLI Args
from cli import ARGS

#Configuration module
from config_parser import ConfigReturn

#Get the config file that has our allowances 
import maestro.lambda_config as lambda_config

#Trigger module
from maestro.triggers import create_trigger as create_trigger
from maestro.triggers import remove_invoke_action as delete_trigger

#DLQ module
from maestro.dlq import get_sns_arn
from maestro.dlq import get_sqs_arn

#Core actions
from maestro.create_lambda import create
from maestro.delete_lambda import delete
from maestro.update_lambda_code import update_code
from maestro.update_lambda_config import update_config
from maestro.publish_lambda import publish
from maestro.invoke import main as invoke
from maestro.alias import alias_creation as alias_creation
from maestro.alias import alias_destroy as alias_destroy
from maestro.alias import alias_update as alias_update

#Everything else
from maestro.security_groups import security_groups as security_groups_method
from maestro.s3_backup import main as s3_backup

from maestro.cloudwatch_sub import cloudwatchSubscription
from maestro.config_validator import validation
from maestro.zip_function import zip_function
from maestro.check_existence import check
from maestro.role_arn import get_arn
from maestro.vpc_location import main as vpc_location

def main():
    '''
    The main entry point for the whole application, first we start out with collection all of the info
    we need from CLI args and json config, then we'll move on to the good stuff
    '''
    #Start by initializing the config class, then let's assign all our variables
    config = ConfigReturn(ARGS)

    #Variable for action
    action = config.get_action()
    
    #Get all of our hard requirements and set them as variables
    name, desc, region, role, handler, runtime, timeout, memsize = config.get_required()
    
    #Get the alias if applicable
    alias = config.get_alias()
    
    #Get the tracing mode, if applicable
    trace_mode = config.get_trace_mode()
    
    #Get the vpc infomation if applicable
    vpc_setting, vpc_name, vpc_security_group_ids = config.get_vpc_setting()
    
    #Get the variable
    variables = config.get_variables()
    
    #Get all DLQ info
    dlq, dlq_type, dlq_target_name = config.get_dlq()

    #Get the tags
    tags = config.get_tags()

    #Triggers, if applicable
    func_trigger_method, func_trigger_source, func_trigger_event_type = config.get_triggers()

    #Logging information
    func_log_forwarding, func_logging_dest ,func_dest_alias = config.get_logging()

    #Backup info
    backup_bucket = config.get_backup()

    #Invoke information
    invoke_type, invoke_version, invoke_payload = config.get_invoke()

    #Do they want to publish?
    publish = config.get_publish()

    #Pass over all publish args, yay or nay?
    no_pub = config.get_no_publish()

    #Get their version description, if they used one
    version_description = config.get_version_description()

    #Get the boolean response of dry run cli arg
    dry_run = config.get_dry_run()
    
############## Do the main thing ##########
if __name__ == '__main__':
    main()