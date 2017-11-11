#External Libs
import json
import os
import sys

#Get CLI Args
from cli import ARGS

#Configuration module
from maestro.config.config_parser import ConfigReturn

#Get the config file that has our allowances 
import maestro.config.lambda_config as lambda_config
from maestro.config.config_validator import validation

#Core actions
from maestro.actions.create import create_action
from maestro.actions.create_alias import create_alias_action
from maestro.actions.delete import delete_action
from maestro.actions.delete_alias import delete_alias_action
from maestro.actions.invoke import invoke_action
from maestro.actions.update_alias import update_alias_action
from maestro.actions.update_code import update_code_action
from maestro.actions.update_config import update_config_action

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