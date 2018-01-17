#External libs
import os
import sys

#Get relevant modules
from maestro.providers.aws.alias import alias_creation
from maestro.providers.aws.check_existence import check
from maestro.providers.aws.cloudwatch_sub import cloudwatchSubscription
from maestro.providers.aws.cloudwatch_logs_expiration import set_cloudwatch_log_expiration
from maestro.providers.aws.create_lambda import create
from maestro.providers.aws.event_stream_trigger import create_event_source
from maestro.providers.aws.triggers import create_trigger
from maestro.providers.aws.s3_backup import main as s3_backup
from maestro.providers.aws.function_concurrency import putFunctionConcurrency

def create_action(name, runtime, region, role, handler, description, timeout, mem_size, invoke_method=False, invoke_source=False, 
                    alias=False, vpc_setting=False, config_vpc_name=False, config_security_groups=False, dry_run=False, 
                    publish=False, variables=False, logging=False, dead_letter_config=False, dlq_type=False, dlq_name=False, 
                    dest_lambda=False, dest_alias=False, event_type=False, tags=False, tracing_mode=False, bucket_name=False, 
                    log_expire=False, event_source=False, event_source_name=False, event_batch_size=False, event_enabled_status=False,
                    event_start_position=False, concurrency_setting=False):
    '''
    Creates a lambda function, first checks to see if it exists, if yes, exit, else, create lambda

    args:
        too many to list, but everything we collect gets passed into this
    '''
    print("Checking to see if lambda already exists")
    if check(name):
      print("This function already exists, please use action 'update'")
      sys.exit(1)
    else:
        #The core action of this function
        create_function = create(
                                lambda_name=name, 
                                runtime=runtime, 
                                role=role, 
                                handler=handler, 
                                description=description, 
                                timeout=timeout, 
                                mem_size=mem_size, 
                                vpc_setting=vpc_setting, 
                                config_vpc_name=config_vpc_name, 
                                config_security_groups=config_security_groups,
                                user_tags=tags,
                                publish=publish,
                                variables=variables,
                                dead_letter_config=dead_letter_config,
                                dlq_type=dlq_type,
                                dlq_name=dlq_name,
                                tracing_mode=tracing_mode,
                                dry_run=dry_run
                                )

        #Check if alias is true, if it is create an alias
        if alias:
            alias_creation(
                            lambda_name=name,
                            new_alias=alias,
                            dry_run=dry_run,
                            publish=publish
                            )
        else:
            pass

        #Check to see if they have any triggers set up 
        if invoke_method:
            create_trigger(
                            lambda_name=name,  
                            invoke_method=invoke_method, 
                            invoke_source=invoke_source, 
                            alias=alias, 
                            event_type=event_type, 
                            dry_run=dry_run
                        )
        else:
            pass

        #Check to see if they're creating an event source mapping
        if event_source:
            create_event_source(
                                source_type=event_source, 
                                source_name=event_source_name, 
                                lambda_name=name, 
                                batch_size=event_batch_size, 
                                enabled=event_enabled_status, 
                                starting_position=event_start_position,
                                alias=alias
                                )
        else:
            pass

        #Check to see if they have logging set up
        if logging:
            cloudwatchSubscription(
                                    newLambdaName=name, 
                                    destLambdaName=dest_lambda, 
                                    destLambdaAlias=dest_alias, 
                                    region=region, 
                                    role=role
                                    )
        else:
            pass
        
        #Check to see if they're setting an expiration on their logs
        if log_expire:
            set_cloudwatch_log_expiration(name=name, retention_time=log_expire)
        else:
            pass

        #Check to see if they're setting up custom concurrency limits
        if concurrency_setting:
            putFunctionConcurrency(functionName=name, reservedCapacity=concurrency_setting)
        else:
            pass

        #Check to see if they want to backup
        if bucket_name:
            s3_backup(
                        lambda_name=name,
                        bucket_name=bucket_name,
                        dry_run=dry_run
                    )
        else:
            pass

        print('Function creation complete!')
