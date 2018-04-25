#External libs
import os
import json
import sys

#Our modules
import maestro.config.lambda_config as lambda_config

#Set up easy to use variables
REGIONS = lambda_config.REGIONS
AVAIL_RUNTIMES = lambda_config.AVAIL_RUNTIMES
ACCEPTED_PROMPT_ACTIONS = lambda_config.ACCEPTED_PROMPT_ACTIONS
DLQ_TYPES = lambda_config.DLQ_TYPES
PRINCIPALS = lambda_config.PRINCIPALS
ACCEPTED_LOG_EXPIRATION = lambda_config.ACCEPTED_LOG_EXPIRATION
EVENT_STREAM_TYPES = lambda_config.EVENT_STREAM_TYPES
EVENT_START_TIMES = lambda_config.EVENT_START_TIMES

def region_helper(region):
    while region not in REGIONS:
        user_region = input("Enter a valid AWS region: ")

        region = user_region

        if region in REGIONS:
            return region
        else:
            pass

def alias_helper(answer):
    while answer not in ACCEPTED_PROMPT_ACTIONS:
        alias_boolean = input("Do you want to set up an alias? (y/n): ")

        answer = alias_boolean

        if answer in ACCEPTED_PROMPT_ACTIONS:
            if answer == 'y':
                alias_name = input("Give your alias a name: ")

                return alias_name
            else:
                return False
        else:
            pass

def trace_helper(trace):
    while not trace:
        tracing_boolean = input("Do you want to enable tracing? (y/n): ")

        answer = tracing_boolean

        if answer in ACCEPTED_PROMPT_ACTIONS:
            if answer == 'y':
                return True
            else:
                return False
        else:
            pass

def runtime_helper(runtime):
    while runtime not in AVAIL_RUNTIMES:
        user_runtime = input("Enter a valid runtime: ")

        runtime = user_runtime

        if runtime in AVAIL_RUNTIMES:
            return runtime
        else:
            pass

def timeout_helper(timeout):
    while timeout not in range(1,301):
        user_timeout = input("Enter a timeout length (in seconds): ")

        timeout = int(user_timeout)

        if timeout in range(1,301):
            return timeout
        else:
            pass

def memsize_helper(memsize):
    while not memsize:
        user_memsize = input("Enter a memory size (in mb): ")

        if int(user_memsize) % 64 == 0:
            if int(user_memsize) < 1536:
                memsize = True
        else:
            memsize = False

        if memsize:
            return int(user_memsize)
        else:
            pass

def security_group_helper(security_group):
    groups = []

    while not security_group:
        security_group = input("Enter the name of a security_group: ")

        groups.append(security_group)

        more_groups = input("Do you want to add another group? (y/n): ")

        if more_groups in ACCEPTED_PROMPT_ACTIONS and more_groups == 'y':
            security_group = False
        else:
            return groups
            security_group = True

def vpc_helper(vpc):
    while not vpc:
        user_vpc = input("Do you want to put this in a vpc? (y/n): ")

        if user_vpc in ACCEPTED_PROMPT_ACTIONS:
            if user_vpc == 'y':
                vpc_name = input("Enter the name of your VPC: ")
                vpc_sgs = security_group_helper(False)

                return vpc_name, vpc_sgs
            else:
                return False, False
        else:
            pass

def variable_looper(looper):
    variable_dict = {}

    while not looper:
        variable_key = input("Enter the variable key: ")
        variable_value = input("Enter the variable value: ")

        variable_dict.update({variable_key: variable_value})

        more_vars = input("Do you want to add another variable? (y/n): ")

        if more_vars in ACCEPTED_PROMPT_ACTIONS and more_vars == 'y':
            looper = False
        else:
            return variable_dict
            looper = True

def variables_helper(variable):
    while not variable:
        user_var = input("Do you want to add variables? (y/n): ")

        if user_var in ACCEPTED_PROMPT_ACTIONS:
            if user_var == 'y':
                var_loop_helper = variable_looper(False)

                return var_loop_helper
            else:
                return False
        else:
            pass

def dlq_decider(configured):
    while not configured:
        dlq_type = input("Enter your DLQ source (sns/sqs): ")

        if dlq_type in DLQ_TYPES:
            dlq_source = input("Enter the name of your DLQ source: ")

            return dlq_type, dlq_source
        else:
            pass

def dlq_helper(dlq):
    dlq_dict = {"type": "", "target_name": ""}

    while not dlq:
        user_dlq = input("Do you want to set up a Dead Letter Queue? (y/n): ")

        if user_dlq in ACCEPTED_PROMPT_ACTIONS:
            if user_dlq == 'y':
                dlq_type, dlq_source = dlq_decider(False)

                dlq_dict['type'] = dlq_type
                dlq_dict['target_name'] = dlq_source

                return dlq_dict
                dlq = True
            else:
                return False
        else:
            pass

def tag_looper(tags):
    tags_dict = {}

    while not tags:
        tag_key = input("Enter your tag key: ")
        tag_value = input("Enter your tag value: ")

        tags_dict.update({tag_key: tag_value})

        more_tags = input("Do you want to add another tag? (y/n): ")

        if more_tags in ACCEPTED_PROMPT_ACTIONS and more_tags == 'y':
            tags = False
        else:
            return tags_dict
            tags = True

def tag_helper(tagged):
    while not tagged:
        user_tag = input("Do you want to add tags? (y/n): ")

        if user_tag in ACCEPTED_PROMPT_ACTIONS:
            if user_tag == 'y':
                tag_dict = tag_looper(False)

                return tag_dict
                tagged = True
            else:
                return False
        else:
            pass

def trigger_decider(decided):
    while not decided:
        get_method = input("Enter your trigger method: (s3/sns/cloudwatch): ")

        if get_method in PRINCIPALS:
            get_source = input("Enter the resource name of your trigger: ")

            return get_method, get_source
            decided = True
        else:
            pass

def trigger_helper(triggered):
    trigger_dict = {"method": "", "source": ""}

    while not triggered:
        user_trigger = input("Do you want to add a trigger? (y/n): ")

        if user_trigger in ACCEPTED_PROMPT_ACTIONS:
            if user_trigger == 'y':
                method, source = trigger_decider(False)

                trigger_dict['method'] = method
                trigger_dict['source'] = source

                return trigger_dict
                triggered = True
            else:
                return False
        else:
            pass

def event_decider(decided):
    while not decided:
        get_method = input("Enter your stream source (kinesis/dynamodb): ")

        if get_method in EVENT_STREAM_TYPES:
            get_source = input("Enter the resource name of your stream: ")

            return get_method, get_source
            decided = True
        else:
            pass

def event_enabled(enabled):
    while not enabled:
        get_enable = input("Would you like to enable this event? (y/n): ")

        if get_enable in ACCEPTED_PROMPT_ACTIONS:
            if get_enable == 'y':
                enabled = "True"
            else:
                enabled = "False"

            return enabled
        else:
            pass

def event_position_helper(positioned):
    while not positioned:
        get_position = input("Enter your start position (LATEST/TRIM_HORIZON/AT_TIMESTAMP): ")

        if get_position in EVENT_START_TIMES:
            return get_position
        else:
            pass

def event_helper(event):
    event_dict = {"type": "", "source": "", "batch_size": "", "enabled": "", "start_position": ""}

    while not event:
        user_event = input("Do you want to set up an event stream map for a trigger? (y/n): ")

        if user_event in ACCEPTED_PROMPT_ACTIONS:
            if user_event == 'y':
                method, source = event_decider(False)

                batch_size = input("Enter a batch size: ")

                enabled = event_enabled(False)

                start_position = event_position_helper(False)

                #Assign them to the dictionary 
                event_dict['type'] = method
                event_dict['source'] = source
                event_dict['batch_size'] = int(batch_size)
                event_dict['enabled'] = enabled
                event_dict['start_position'] = start_position

                return event_dict
                event = True
            else:
                return False
        else:
            pass

def log_helper(helped):
    log_forward_dict = {"destination_lambda": "", "destination_alias": ""}

    while not helped:
        user_helper = input("Do you want to set up a Cloudwatch Log Subscription? (y/n): ")

        if user_helper in ACCEPTED_PROMPT_ACTIONS:
            if user_helper == 'y':
                dest_name = input("Enter the name of your destination lambda: ")
                dest_alias = input("Enter the name of your destination alias: ")

                log_forward_dict['destination_lambda'] = dest_name
                log_forward_dict['destination_alias'] = dest_alias

                return log_forward_dict
                helped = True
            else:
                return False
        else:
            pass

def log_exire_looper(valid_age):
    while not valid_age:
        user_age = input("How long do you want to keep your logs? (in days): ")

        if int(user_age) in ACCEPTED_LOG_EXPIRATION:
            return int(user_age)
            valid_age = True
        else:
            pass

def log_expire_helper(expired):
    log_exp_dict = {"age": ""}

    while not expired:
        user_expire = input("Do you want to setup log expiration for your Cloudwatch logs? (y/n): ")

        if user_expire in ACCEPTED_PROMPT_ACTIONS:
            if user_expire == 'y':
                age = log_exire_looper(False)

                log_exp_dict['age'] = age

                return log_exp_dict
                expired = True
            else:
                return False
        else:
            pass

def backup_helper(backed_up):
    backup_dict = {"bucket_name": ""}

    if not backed_up:
        user_backup = input("Do you want to set up a backup bucket? (y/n): ")

        if user_backup in ACCEPTED_PROMPT_ACTIONS:
            if user_backup == 'y':
                bucket_name = input("Enter your bucketname: ")

                backup_dict['bucket_name'] = bucket_name 

                return backup_dict
                backed_up = True
            else:
                return False
        else:
            pass

def write_file(json_obj, filename=None):
    current_dir = os.getcwd()

    full_path = os.path.join(current_dir, filename)

    f = open(full_path, 'w')

    f.write(json.dumps(json_obj, indent=4))

    f.close()


def initialize(filename):
    #Start out with the barebones of what you need
    empty_dict = {"initializers": {}, "provisioners": {}}

    #Get the lambda name
    lambda_name = input("what do you want to call your lambda? ")

    empty_dict['initializers'].update({"name": lambda_name})

    #Get the description
    lambda_desc = input("Enter a description for your lambda: ")

    empty_dict['initializers'].update({"description": lambda_desc})

    #Get the region
    region_help = region_helper('region')

    if region_help:
        empty_dict['initializers'].update({"region": region_help})

    #Get the handler
    lambda_hand = input("Enter your lambda handler: ")

    empty_dict['initializers'].update({"handler": lambda_hand})

    #Get the role
    lambda_role = input("Enter the role you'd like to use: ")

    empty_dict['initializers'].update({"role": lambda_role})

    #Ask about alias
    alias_help = alias_helper('maybe')

    if alias_help:
        empty_dict['initializers'].update({"alias": alias_help})
    else:
        pass

    #Tracing
    trace_help = trace_helper(False)

    if trace_help:
        empty_dict['initializers'].update({"tracing_mode": "active"})
    else:
        pass

    '''
    Provisioner questions
    '''
    #Runtime
    runtime_help = runtime_helper('runtime')

    if runtime_help:
        empty_dict['provisioners'].update({"runtime": runtime_help})

    #Timeout
    timeout_help = timeout_helper(1000)

    if timeout_help:
        empty_dict['provisioners'].update({"timeout": timeout_help})

    #Memsize
    memsize_help = memsize_helper(False)

    if memsize_help:
        empty_dict['provisioners'].update({"mem_size": memsize_help})

    '''
    All below is optional
    '''
    #VPC Info
    vpc_help_name, vpc_help_sgs = vpc_helper(False)

    if vpc_help_name:
        empty_dict.update({"vpc_setting": {"vpc_name": vpc_help_name, "security_group_ids": vpc_help_sgs}})
    else:
        pass

    #Variables
    variables_help = variables_helper(False)

    if variables_help:
        empty_dict.update({"variables": variables_help})
    else:
        pass

    #Dead letter config
    dlq_help = dlq_helper(False)

    if dlq_help:
        empty_dict.update({"dead_letter_config": dlq_help})
    else:
        pass

    #Tags
    tags_help = tag_helper(False)

    if tags_help:
        empty_dict.update({"tags": tags_help})
    else:
        pass

    #Triggers
    trig_help = trigger_helper(False)

    if trig_help:
        empty_dict.update({"trigger": trig_help})
    else:
        pass

    #Event Stream Mapping
    event_help = event_helper(False)

    if event_help:
        empty_dict.update({"event_stream": event_help})
    else:
        pass

    #Logging
    log_help = log_helper(False)

    if log_help:
        empty_dict.update({"logging": log_help})
    else:
        pass

    #Log Expiration
    log_exp_help = log_expire_helper(False)

    if log_exp_help:
        empty_dict.update({"log_expiration": log_exp_help})
    else:
        pass

    #Backup
    backup_help = backup_helper(False)

    if backup_help:
        empty_dict.update({"backup": backup_help})
    else:
        pass

    #Write file
    write_file(empty_dict, filename=filename)

    sys.exit(0)