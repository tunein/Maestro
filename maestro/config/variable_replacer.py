import json
import os
import sys

def get_variables(user_dict):
    '''
    Get the variables from the config file, here we're looking to see if they're using any variables
    If they are using variables then we'll append them to a list for using to validate against what is past
    in the CLI

    args:
        user_dict: the dictionary of variables the user placed in the file
    '''
    variables = []

    for key, value in user_dict.items():
        if value.startswith("${var."):
            variable = value.split("${var.")[1].replace("}", "")
            variables.append(variable)
        else:
            pass

    if len(variables) != 0:
        variables = variables
    else:
        variables = None

    return variables

def var_args_dict(vars):
    '''
    Helper function. Takes our list of tuples of variables from the CLI and returns it as a dictionary

    args:
        vars: a list of tuples retrieved from the CLI
    '''
    var_dict = dict(vars)

    return var_dict

def validate_args(var_dict, var_list):
    '''
    Validates that the arguments in the CLI and the dictionary match, raises an error if not
    This is here for validation only

    args:
        var_dict: the dictionary we put together from the cli args
        var_list: list of variables we need to replace
    '''
    for var in var_list:
        if var in var_dict:
            print("CLI argument %s validated" % var)
        else:
            print("Some variables do not match, please check your configuration and try again")
            sys.exit(1)

def replace_args(config_dict, var_dict):
    '''
    Does the actual replacing of the variables in the dictionary, returns a dictionary with variables replaced

    args:
        config_dict: our original dictionary pulled from the config file
        var_dict: our newly created dictionary, pulled form the CLI
    ''' 
    print("Replacing variables")

    for secret_key, new_value in var_dict.items():
        for key, value in config_dict.items():
            if value == '${var.%s}' % secret_key:
                config_dict[key] = new_value
            else:
                pass

    return config_dict

####### Main Entrypoint#######
def variable_replacer(variable_dict, user_variables):
    '''
    main entrypoint for the variable replacer module, takes a dictionary of variables 

    args:
        variable_dict: the user's dictionary of variables
    '''
    variables = get_variables(variable_dict)

    if variables is not None:
        cli_variables = var_args_dict(user_variables)
        validation = validate_args(var_dict=variables, var_list=cli_variables)
        new_config = replace_args(variable_dict, cli_variables)
    else:
        new_config = variable_dict

    return new_config
