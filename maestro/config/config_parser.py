#External libs
import json
import os
import sys

#Grab our variable replacer
from maestro.config.variable_replacer import variable_replacer

class ConfigParser(object):
    '''
    Provides a simple interface for retrieving items from config file, and the more complex ones from CLI
    '''
    def __init__(self, config_file):
        self.config_file = config_file

    def get_section(self, section):
        '''
        Let's us check to see if a section exists, used to check for optional items in config
        '''
        with open(self.config_file) as json_data:
            read = json.load(json_data)
            output = read.get(section, None)

            if output is None:
                output = False

            return output

    def get_section_item(self, section, parameter):
        '''
        Grabs specific items from the config file for us
        '''
        with open(self.config_file) as json_data:
            read = json.load(json_data)
            section = read.get(section, None)

            if section:
                return section.get(parameter)
            return False

############# Entry point #####################
class ConfigReturn(ConfigParser):
    '''
    this is here for the sake of returning some simple to the main entry point module

    the goal of this entire module is to return configuration settings whether they come from
    the config file or the CLI in a uniform way.
    '''
    def __init__(self, cli_args):
        self.cli_args = cli_args
        self.config_file = self.cli_args.filename

        ConfigParser.__init__(self, self.config_file)

    def get_action(self):
        '''
        Return the action, duh
        '''
        action = self.cli_args.action
        return action

    def get_required(self):
        '''
        Returning our required items in an organized way to the main function
        '''
        func_name = super().get_section_item('initializers', 'name')
        func_description = super().get_section_item('initializers', 'description')
        func_region = super().get_section_item('initializers', 'region')
        func_role = super().get_section_item('initializers', 'role')
        func_handler = super().get_section_item('initializers', 'handler')
        func_runtime = super().get_section_item('provisioners', 'runtime')
        func_timeout = super().get_section_item('provisioners', 'timeout')
        func_mem_size = super().get_section_item('provisioners', 'mem_size')

        return func_name, func_description, func_region, func_role, func_handler, func_runtime, func_timeout, func_mem_size


    def get_alias(self):
        '''
        return alias
        '''
        if super().get_section_item('initializers', 'alias'):
            func_alias = super().get_section_item('initializers', 'alias')
        else:
            func_alias = self.cli_args.alias

        return func_alias

    def get_trace_mode(self):
        '''
        Check to see if they're using tracing for their lambda
        '''
        if super().get_section_item('initializers', 'tracing_mode'):
            func_trace_mode = super().get_section_item('initializers', 'tracing_mode')
        else:
            func_trace_mode = False

        return func_trace_mode

    def get_vpc_setting(self):
        '''
        Check to see if they're using VPC setting, vpc_name and security groups default to false
        '''
        if super().get_section('vpc_setting'):
            func_vpc_setting = True
            func_vpc_name = super().get_section_item('vpc_setting', 'vpc_name')
            func_security_group_ids = super().get_section_item('vpc_setting', 'security_group_ids')
        else:
            func_vpc_setting = False
            func_vpc_name = False
            func_security_group_ids = False

        return func_vpc_setting, func_vpc_name, func_security_group_ids

    def get_variables(self):
        '''
        Check to see if they're using Variables, we just want the whole dictionary, if not everything defaults to false
        '''
        if super().get_section('variables'):
            func_variables = super().get_section('variables')
        else:
            func_variables = False

        replaced_variables = variable_replacer(func_variables, self.cli_args.var)

        return replaced_variables

    def get_dlq(self):
        '''
        #Check to see if they're using a DLQ, if not set to false
        '''
        if super().get_section('dead_letter_config'):
            func_dlq = True
            func_dlq_type = super().get_section_item('dead_letter_config', 'type')
            func_dlq_target_name = super().get_section_item('dead_letter_config', 'target_name')
        else:
            func_dlq = False
            func_dlq_type = False
            func_dlq_target_name = False

        return func_dlq, func_dlq_type, func_dlq_target_name

    def get_tags(self):
        '''
        Check to see if they want tags, we just want the whole dictionary
        '''
        if super().get_section('tags'):
            tags = super().get_section('tags')
        else:
            tags = False

        return tags

    def get_triggers(self):
        '''
        Check to see if they're using triggers, if they aren't in the config they default to CLI args
        '''
        if super().get_section('trigger'):
            func_create_trigger = self.cli_args.create_trigger
            func_trigger_method = super().get_section_item('trigger', 'method')
            func_trigger_source = super().get_section_item('trigger', 'source')
            func_trigger_event_type =super().get_section_item('trigger', 'event_type')
        else:
            func_create_trigger = self.cli_args.create_trigger
            func_trigger_method = self.cli_args.invoke_method
            func_trigger_source = self.cli_args.invoke_source
            func_trigger_event_type = self.cli_args.event_type

        return func_create_trigger, func_trigger_method, func_trigger_source, func_trigger_event_type

    def get_event_mapping(self):
        '''
        Check to see if they're using event streams
        '''
        if super().get_section('event_stream'):
            func_event_source = super().get_section_item('event_stream', 'type')
            func_event_source_name = super().get_section_item('event_stream', 'source')
            func_event_batch_size = super().get_section_item('event_stream', 'batch_size')
            func_event_enable_status = super().get_section_item('event_stream', 'enabled')
            func_event_start_position = super().get_section_item('event_stream', 'start_position')

            if func_event_enable_status.lower() == "true":
                func_event_enable_status = True
            else:
                func_event_enable_status = False
        else:
            func_event_source = False
            func_event_source_name = False
            func_event_batch_size = False
            func_event_enable_status = False
            func_event_start_position = False

        return func_event_source, func_event_source_name, func_event_batch_size, func_event_enable_status, func_event_start_position

    def get_logging(self):
        '''
        Check to see if they're forwarding their cloudwatch logs to a processing lambda
        '''
        if super().get_section('logging'):
            func_log_forwarding = True
            func_logging_dest = super().get_section_item('logging', 'destination_lambda')
            func_dest_alias = super().get_section_item('logging', 'destination_alias')
        else:
            func_log_forwarding = False
            func_logging_dest = False
            func_dest_alias = False

        return func_log_forwarding, func_logging_dest, func_dest_alias

    def get_logging_expiration(self):
        '''
        Check to see if they're setting up a log expiration policy
        '''
        if super().get_section('log_expiration'):
            func_log_expiration = super().get_section_item('log_expiration', 'age')
        else:
            func_log_expiration = False

        return func_log_expiration

    def get_backup(self):
        '''
        Check to see if they're backing their deploys up to s3
        '''
        if super().get_section('backup'):
            func_backup_bucket = super().get_section_item('backup', 'bucket_name')
        else:
            func_backup_bucket = False

        return func_backup_bucket

    def get_invoke(self):
        '''
        Invoke specific variables
        '''
        invoke_type = self.cli_args.invoke_type
        invoke_version = self.cli_args.version
        invoke_alias = self.cli_args.alias
        invoke_payload = self.cli_args.payload

        return invoke_type, invoke_version, invoke_alias, invoke_payload

    def get_publish(self):
        '''
        Return status of publish cli arg
        '''
        publish = self.cli_args.publish

        return publish

    def get_no_publish(self):
        '''
        return status of no pub cli arg
        '''
        no_pub = self.cli_args.no_pub

        return no_pub

    def get_version_description(self):
        '''
        gets version description from CLI arg and returns it
        '''
        version_description = self.cli_args.version_description

        return version_description

    def get_delete_trigger(self):
        '''
        gets the boolean response of --delete_trigger
        '''
        remove_trigger = self.cli_args.delete_trigger

        return remove_trigger

    def get_dry_run(self):
        '''
        Dry run argument, turns everything to what is essentially a "just print the output" mode
        '''
        dry_run = self.cli_args.dry_run

        return dry_run