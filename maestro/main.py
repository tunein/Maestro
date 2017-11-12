#External Libs
import json
import os
import sys

#Get CLI Args
from maestro.cli import ARGS

#Configuration module
from maestro.config.config_parser import ConfigReturn

#Get the config file that has our allowances 
import maestro.config.lambda_config as lambda_config

#Validators
from maestro.config.config_validator import validate_file_type
from maestro.config.config_validator import validate_action
from maestro.config.config_validator import validate_runtime
from maestro.config.config_validator import validate_role
from maestro.config.config_validator import validate_timeout

#Core actions
from maestro.actions.create import create_action
from maestro.actions.create_alias import create_alias_action
from maestro.actions.delete import delete_action
from maestro.actions.delete_alias import delete_alias_action
from maestro.actions.invoke import invoke_action
from maestro.actions.publish import publish_action
from maestro.actions.update_alias import update_alias_action
from maestro.actions.update_code import update_code_action
from maestro.actions.update_config import update_config_action

def main():
    '''
    The main entry point for the whole application, first we start out with collection all of the info
    we need from CLI args and json config, then we'll move on to the good stuff
    '''
    #Validate the filetype, should end with '.json'
    validate_file_check = validate_file_type(ARGS.filename)

    #initializing the config class, then let's assign all our variables
    config = ConfigReturn(ARGS)

    #Variable for action
    action = config.get_action()

    #validate the action
    validate_action_check = validate_action(action)
    
    #Get all of our hard requirements and set them as variables
    name, desc, region, role, handler, runtime, timeout, memsize = config.get_required()
    
    #Validate runtime, role, and timeout
    validate_runtime_check = validate_runtime(runtime)
    validate_role_check = validate_role(role)
    validate_timeout_check = validate_timeout(timeout)

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
    '''
    Now that we've retrieved all over our actions let's run things for real
    '''
    if action == 'create':
        print('Attempting to create')
        create_action(name=name, runtime=runtime, region=region, role=role, handler=handler, description=desc, 
                    timeout=timeout, mem_size=memsize, alias=alias, vpc_setting=vpc_setting, config_vpc_name=vpc_name, 
                    config_security_groups=vpc_security_group_ids, dry_run=dry_run, publish=publish, variables=variables, 
                    logging=func_log_forwarding, dead_letter_config=dlq, dlq_type=dlq_type, dlq_name=dlq_target_name, 
                    dest_lambda=func_logging_dest, dest_alias=func_dest_alias, event_type=func_trigger_event_type, tags=tags, 
                    tracing_mode=trace_mode, bucket_name=backup_bucket, invoke_method= func_trigger_method,
                    invoke_source=func_trigger_source)

    elif action == 'create-alias':
        create_alias_action(args, it, needs, here)

    elif action == 'delete':
        delete_action(args, it, needs, here)

    elif action == 'delete-alias':
        delete_alias_action(args, it, needs, here)

    elif action == 'invoke':
        invoke_action(args, it, needs, here)

    elif action == 'publish':
        publish_action(args, it, needs, here)

    elif action == 'update-code':
        update_code_action(args, it, needs, here)

    elif action == 'update-config':
        update_config_action(args, it, needs, here)
        
    elif action == 'update-alias':
        update_alias_action(args, it, needs, here)

############## Do the main thing BABY ##########
if __name__ == '__main__':
    main()