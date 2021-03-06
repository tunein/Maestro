#External libs
import os
import sys

#Get relevant modules
from maestro.providers.aws.check_existence import check
from maestro.providers.aws.cloudwatch_logs_expiration import set_cloudwatch_log_expiration
from maestro.providers.aws.event_stream_trigger import create_event_source
from maestro.providers.aws.event_stream_trigger import check_source_mapping
from maestro.providers.aws.event_stream_trigger import update_event_source
from maestro.providers.aws.get_policy import get_lambda_policy
from maestro.providers.aws.triggers import create_trigger
from maestro.providers.aws.triggers import remove_trigger
from maestro.providers.aws.update_lambda_config import update_config
from maestro.providers.aws.function_concurrency import putFunctionConcurrency

def update_config_action(name, handler, description, timeout, mem_size, runtime, role, alias=False, vpc_setting=False, vpc_name=False, 
                        vpc_security_groups=False, tags=False, variables=False, dlq=False, dlq_type=False, dlq_name=False, 
                        tracing_mode=False, create_trigger_bool=False, remove_trigger_bool=False, invoke_method=False, 
                        invoke_source=False, event_type=False, dry_run=False, log_expire=False, event_source=False,
                        event_source_name=False, event_batch_size=False, event_enabled_status=False, event_start_position=False,
                        concurrency_setting=False):
    '''
    Updates the configuration of the given lambda, this has all the same parameters as the create function with the
    exception of updating code. Every single parameter (except code) can be changed using this. 

    This module is also used to add or delete triggers from the CLI.

    args:
        too many to list, but all of them except for updating code
    '''
    if check(name):

        update_config(lambda_name=name, handler=handler, description=description, timeout=timeout, mem_size=mem_size, 
                    runtime=runtime, role=role, vpc_setting=vpc_setting, config_vpc_name=vpc_name, 
                    config_security_groups=vpc_security_groups, new_tags=tags, variables=variables, dead_letter_config=dlq, 
                    dlq_type=dlq_type, dlq_name=dlq_name, tracing_mode=tracing_mode)

        if remove_trigger_bool:
            remove_trigger(lambda_name=name, alias=alias, invoke_source=invoke_source)
            sys.exit(0)
        else:
            pass

        #Check to see if they're setting an expiration on their logs
        if log_expire:
            set_cloudwatch_log_expiration(name=name, retention_time=log_expire)
        else:
            pass

        #Check to see if they have a trigger in their config
        if create_trigger_bool or invoke_method:

            #Grab the current policy, we'll validate against this to make sure the policy doesn't exit already
            current_trigger_list = get_lambda_policy(name=name, alias=alias)

            if current_trigger_list:
                if all(item in current_trigger_list for item in [alias, invoke_method, invoke_source]):
                    print('Trigger exists already, exiting gracefully')
                    sys.exit(0)
            create_trigger(lambda_name=name, invoke_method=invoke_method, invoke_source=invoke_source, alias=alias, 
                            event_type=event_type, dry_run=dry_run)

        #Check to see if they're creating/updating an event source mapping
        if event_source:
            if check_source_mapping(source_type=event_source, source_name=event_source_name, lambda_name=name, alias=alias):
                #If check_source_mapping returns true it means we have confirmed we've got the event stream already setup

                update_event_source(source_type=event_source, source_name=event_source_name, lambda_name=name, 
                                    batch_size=event_batch_size, enabled=event_enabled_status, alias=alias)
            else:
                #If check source mapping returns False it means we need create the mapping

                create_event_source(source_type=event_source, source_name=event_source_name, lambda_name=name, 
                                    batch_size=event_batch_size, enabled=event_enabled_status, starting_position=event_start_position,
                                    alias=alias)
        else:
            pass

        #Check to see if they're setting up custom concurrency limits
        if concurrency_setting:
            putFunctionConcurrency(functionName=name, reservedCapacity=concurrency_setting)
        else:
            putFunctionConcurrency(functionName=name)

        print('Function configuration update complete!')
    else:
        print('Lambda "%s" not found!' % name)
        sys.exit(1)
