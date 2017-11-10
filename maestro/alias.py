#External libs
import boto3
import sys
import json
import os
from botocore.exceptions import ClientError

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

#Establish our boto resources
client = boto3.client('lambda')
iam = boto3.resource('iam')
roles = boto3.client('iam')

def alias_creation(lambda_name, new_alias=False, dry_run=False, publish=False):
    '''
    Creates an alias, does a set of checks first to ensure the alias doesn't exist, if it does
    it prompts you to update the alias, this manual step can be passed over using the '--publish' CLI arg

    args:
        lambda_name: name of the lambda, retrieved from config file
        alias: name of alias you'd like to create, pulled from config or CLI
        dry_run: CLI arg denoting the user just wants to see what would happen, not actually do it 
        publish: CLI arg denoting the user doesn't want to be prompted
    '''
    alias = client.list_aliases(
        FunctionName='%s' % lambda_name,
        )

    dump_json = json.dumps(alias, indent=4) 
    load = json.loads(dump_json)

    aliases = []

    for names in load['Aliases']:    
        aliases.append(names['Name'])

    #Get the alias, and check if it exists on the lambda already
    if new_alias:
        if new_alias in aliases:
            if publish:
                if alias_update():
                    return True
            else:
                ask = input("Alias exists, would you like to update it (y/n)? ")
                if ask == 'y':
                    if alias_update():
                        print("Attempting to update alias %s" % new_alias)
                        return True
                    else:
                        return False
                else:
                    print("Exiting!")
                    sys.exit(1)  
        else:
            if dry_run:
                alias_name = alias
                print(color.PURPLE + "***Dry run option enabled***" + color.END)
                print(color.PURPLE + "Would have created alias: %s for %s" % (alias, lambda_name) + color.END)
            else:
                alias_name = new_alias
                pass
    else:
        #Prompt the user to fill in the info 
        get_alias_name = input("What would you like this alias to be called? ")
        alias_name = get_alias_name.lower()
        if alias_name in aliases:
            ask = input("Alias exists, would you like to update it (y/n)? ")
            if ask == 'y':
                if alias_update():
                    print("Attempting to update alias %s" % alias)
                    return True
                else:
                    return False
            else:
                print("Exiting!")
                sys.exit(1)

    #Get list of current versions of lambda, put it in an array so we can validate the user inputted version
    versions = client.list_versions_by_function(
                                        FunctionName='%s' % lambda_name,
                                    )

    version_json = json.dumps(versions, indent=4)
    load_json = json.loads(version_json)
    versions = load_json['Versions']
    avail_versions = []

    for version in versions:
        if version['Version'] != 0:
            print('version: %s' % version['Version'])
            avail_versions.append(version['Version'])

    if publish:
        function_version = max(avail_versions)
    else:
        function_version = input("What version would you like to create an alias for? ")
    
    if dry_run:
        print(color.PURPLE + "Dry run creating alias '%s' for version '%s' on lambda '%s'" % (alias_name, function_version, lambda_name) + color.END)
        return True
    else:
        pass

    #This is the actual action, creates an alias for the specific version, first we validate the version exists
    if function_version in avail_versions: 
        try:
            add_alias = client.create_alias(
                FunctionName='%s' % lambda_name,
                Name='%s' % alias_name,
                FunctionVersion='%s' % function_version,
            )
            if add_alias['ResponseMetadata']['HTTPStatusCode'] == 201:
                print("Adding alias '%s' to lambda '%s' version '%s'" % (alias_name, lambda_name, function_version))
                return True
            else:
                return False
        except ClientError as error:
            print(error.response['Error']['Message'])
    else:
        print("I can't find that version, check list and find again")

def alias_destroy(lambda_name, del_alias=False, dry_run=False):
    '''
    Destroys specified alias, this will probably only get used for breaking changes and accidents
    but it is good to have anyway...

    args:
        lambda_name: name of the lambda containing the alias, retrieved from config file
        alias: alias pulled from CLI arg, the one to be deleted
        dry_run: CLI arg to denote the user only wants to see what would happen
    '''
    alias = client.list_aliases(
        FunctionName='%s' % lambda_name,
        )

    dump_json = json.dumps(alias, indent=4) 
    load = json.loads(dump_json)

    aliases = []

    #Load the existing aliases into an array so we can validate we're deleting a real alias
    for names in load['Aliases']:
        print("Function Version: '%s', Alias: '%s'" % (names['FunctionVersion'], names['Name']))
        aliases.append(names['Name'])

    if len(aliases) != 0:
        if del_alias:
            alias_name = del_alias
        else:
            alias_name = input("What alias would you like to delete? ")

        #This is the important part, validates then deletes the alias (if we aren't dry running)
        if alias_name in aliases:
            if dry_run:
                print(color.PURPLE + "***Dry run option enabled***" + color.END)
                print(color.PURPLE + "Dry run deleting alias %s on %s" % (alias_name, lambda_name) + color.END)
                return True
            else:
                try:
                    delete_alias = client.delete_alias(
                            FunctionName='%s' % lambda_name,
                            Name='%s' % alias_name
                    )
                    print("Alias successfully deleted")
                    return True
                except ClientError as error:
                    print(error.response['Error']['Message'])
        else:
            print("That alias does not exist, please check the list of existing aliases and try again")
    else:
        print("No aliases found..")

def alias_update(lambda_name, new_alias=False, dry_run=False, publish=False):
    '''
    Updates an existing alias to use a new version of code
    This can be called by itself or if the user tries to create an alias and it already exists, this will get called

    args:
        lambda_name: name of the lambda, retrieved from the config file
        alias: alias we want to update, retrieved from config file or CLI arg
        dry_run: CLI arg to denote the user only wants to see what would happen
        publish: CLI arg to pass over all prompts, this defaults the alias to the newest version (denoted by highest version number)
    '''

    # Create a list of available versions, $LATEST == 0
    versions = client.list_versions_by_function(
                                        FunctionName='%s' % lambda_name,
                                    )

    version_json = json.dumps(versions, indent=4)
    load_json = json.loads(version_json)
    versions = load_json['Versions']
    avail_versions = []

    for version in versions:
        if version['Version'] != 0:
            version = version['Version']
            if version == "$LATEST":
                version = 0
                avail_versions.append(version)
            else:
                avail_versions.append(version)

    # Create a list of aliases, used for validating the passed alias
    alias = client.list_aliases(
        FunctionName='%s' % lambda_name,
        )

    dump_json = json.dumps(alias, indent=4) 
    load = json.loads(dump_json)

    aliases = []

    for names in load['Aliases']:
        print("Function Version: '%s' has alias: '%s'" % (names['FunctionVersion'], names['Name']))     
        aliases.append(names['Name'])
    print("\n")

    if len(aliases) != 0:
        if new_alias:
            alias_name = new_alias
        else:
            alias_name = input("What alias would you like to update? ")

        if publish:
            '''
            If the user rolls over prompts using 'publish' we automatically update the alias
            to use the highest available version integer (the newest version of code)
            '''
            largest = max(avail_versions, key=int)
            if largest == 0:
                version_update = '$LATEST'
            else:
                version_update = largest
        else:
            for version in avail_versions:
                print("Version: " + str(version))

            version_update = input("What version would you like to assign the updated alias to? ")

        #This is the main action, first we validate alias and version, then we do it for real 
        if alias_name in aliases:
            if version_update in avail_versions:
                if version_update == 0:
                    version_update == "$LATEST"
                else:
                    pass
                if dry_run:
                    print(color.PURPLE + "***Dry run option enabled***" + color.END)
                    print(color.PURPLE + "Would have updated update alias '%s' on version '%s' on lambda '%s'" % (alias_name, version_update, lambda_name) + color.END)
                    return True
                else:
                    try:
                        update_alias = client.update_alias(
                                                        FunctionName='%s' % lambda_name,
                                                        Name='%s' % alias_name,
                                                        FunctionVersion='%s' % version_update,
                                                    )
                        if update_alias['ResponseMetadata']['HTTPStatusCode'] == 200:
                            print("Lamda '%s' version '%s' alias '%s' has been updated!" % (lambda_name, version_update, alias_name))
                            return True
                        else:
                            return False
                    except ClientError as error:
                        print(error.response['Error']['Message'])
            else:
                print("Version not found..")
        else:
            print("No aliases found...")
