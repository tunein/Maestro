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
    alias_name = ""

    for names in load['Aliases']:    
        aliases.append(names['Name'])

    #Get the alias, and check if it exists on the lambda already
    if new_alias:
        if new_alias in aliases:
            if publish:
                if alias_update(lambda_name, new_alias, dry_run, publish):
                    return True
            else:
                ask = input("Alias exists, would you like to update it (y/n)? ")
                if ask == 'y':
                    if alias_update(lambda_name, new_alias, dry_run, publish):
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

def get_current_alias_version(lambda_name, alias=None):
    '''
    Retrieves current version the specified alias is using
    This is used to keep a lambda at the desired version while weighting traffic across other versions
    
    Example, version 1 is retrieving prod traffic, you push version 2, weight traffic and discover a bug..
    so you push version 3, this keeps the majority of traffic on version 1

    args:
        lambda_name: name of the lambda we're working with
        alias: name of the alias we're working with
    '''
    if alias is not None:
        try:
            config = client.get_alias(
                                FunctionName=lambda_name,
                                Name=alias
                        )
        except ClientError as error:
            print(error)
            sys.exit(1)
        else:
            if config['FunctionVersion']:
                version = config['FunctionVersion']
            else:
                print('Error! Could not find requested aliases function version!')
                sys.exit(1)
        finally:
            return version
    else:
        raise ValueError('You must supply an alias!')

def update_alias_non_weighted(lambda_name, alias=False, version=False):
    '''
    Updates an alias that doesn't have a weight, specifically for used because $LATEST cant split traffic

    args:
        lambda_name: name of the lambda
        alias: name of the alias 
        version: version number
    '''
    try:
        update_alias = client.update_alias(
                                        FunctionName=lambda_name,
                                        Name=alias,
                                        FunctionVersion=version
                                        )
        if update_alias['ResponseMetadata']['HTTPStatusCode'] == 200:
            print('Updated alias %s to version %s' % (alias, version))
            return True
        else:
            return False
    except ClientError as error:
        print(error.response['Error']['Message'])

def update_alias_weighted(lambda_name, alias=False, new_version=False, old_version=False, weight=False):
    '''
    Updates an alias for slowly bringing a new version, keeps the old alias as main, new as the "canary"
    
    args:
        lambda_name: name of lambda
        alias: alias
        new_version: newest version of the lambda 
        old_version: the present primary version with the majority of traffic
        weight: float between 0.0 and 1.0
    '''
    if weight:
        weight_new = weight
    else:
        weight_new = 0.0

    try:
        update_alias = client.update_alias(
                                        FunctionName=lambda_name,
                                        Name=alias,
                                        FunctionVersion=old_version,
                                        RoutingConfig={
                                            'AdditionalVersionWeights': {
                                                new_version: weight_new
                                            }
                                        }
                                    )
        if update_alias['ResponseMetadata']['HTTPStatusCode'] == 200:
            print('Weighting version %s to receive %0.2f of traffic, version %s recieves remaining traffic' % (new_version, float(weight * 100), old_version))
            return True
        else:
            return False
    except ClientError as error:
        print(error.response['Error']['Message'])

def publish_alias_weighted(lambda_name, alias=False, new_version=False, old_version=False, weight=False):
    '''
    Updates an alias that has an existing weighted alias to have the newest version as primary

    args:
        lambda_name: name of lambda
        alias: alias
        new_version: newest version of the lambda 
        old_version: the present primary version with the majority of traffic
        weight: float between 0.0 and 1.0
    '''
    if weight:
        weight_new = weight
    else:
        weight_new = 0.0

    try:
        update_alias = client.update_alias(
                                        FunctionName=lambda_name,
                                        Name=alias,
                                        FunctionVersion=new_version,
                                        RoutingConfig={
                                            'AdditionalVersionWeights': {
                                                old_version: weight_new
                                            }
                                        }
                                    )
        if update_alias['ResponseMetadata']['HTTPStatusCode'] == 200:
            print('Updated alias %s to version %s' % (alias, new_version))
            return True
        else:
            return False
    except ClientError as error:
        print(error.response['Error']['Message'])

def alias_update(lambda_name, update_alias=False, dry_run=False, publish=False, weight=False):
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

    versions = versions['Versions']

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

    aliases = []

    for names in alias['Aliases']:
        print("Function Version: '%s' has alias: '%s'" % (names['FunctionVersion'], names['Name']))     
        aliases.append(names['Name'])
    print("\n")

    if len(aliases) != 0:
        if update_alias:
            alias_name = update_alias
        else:
            alias_name = input("What alias would you like to update? ")

        if publish:
            '''
            If the user rolls over prompts using 'publish' we automatically update the alias
            to use the highest available version integer (the newest version of code)
            '''
            largest = max(avail_versions, key=int)
            version_update = largest
        else:
            for version in avail_versions:
                print("Version: " + str(version))

            version_update = input("What version would you like to assign the updated alias to? ")

        #This is the main action, first we validate alias and version, then we do it for real 
        if alias_name in aliases:

            # Check if we're weighting a new version 
            if weight:
                weight = int(weight) / 100
                weight_version_update = version_update

                # Grab the current function version
                version_2_update = get_current_alias_version(lambda_name, alias=alias_name)

                if version_2_update == "$LATEST":
                    print("Can't split traffic between version $LATEST and new version, updating alias to point to %s" % weight_version_update)
                    update_alias_non_weighted(lambda_name, alias=alias_name, version=version_update)
                else:
                    update_alias_weighted(lambda_name, alias=alias_name, new_version=version_update, old_version=version_2_update, weight=weight)

            else:
                if version_update == 0:
                    version_2_update = "$LATEST"
                    update_alias_non_weighted(lambda_name, alias=alias_name, version=version_2_update)
                elif avail_versions[-2] == 0:
                    update_alias_non_weighted(lambda_name, alias=alias_name, version=version_update)
                else:
                    old_version = avail_versions[-2]
                    publish_alias_weighted(lambda_name, alias=alias_name, new_version=version_update, old_version=old_version)                
            '''
            if dry_run:
                print(color.PURPLE + "***Dry run option enabled***" + color.END)
                print(color.PURPLE + "Would have updated update alias '%s' on version '%s' on lambda '%s'" % (alias_name, version_update, lambda_name) + color.END)
                return True
            else:
            '''        
        else:
            print("No aliases found...")
