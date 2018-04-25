#External libs
import boto3
import json
from botocore.exceptions import ClientError

#Our modules
from maestro.providers.aws.check_existence import check

#Establish our boto resources
client = boto3.client('lambda')

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

def delete(lambda_name, dry_run=False):
    '''
    Handles the deletion of lambdas

    args:
        lambda_name: name of lambda, retrieved from config file
        dry_run: boolean, taken from CLI args
    '''
    if dry_run:
        #Print out all of the things the user would delete if they were to delete
        try:
            print(color.PURPLE + "***Dry run option enabled, dry running a deletion***" + color.END)
            alias = client.list_aliases(
                                            FunctionName='%s' % lambda_name,
                                            )

            dump_json = json.dumps(alias, indent=4) 
            load = json.loads(dump_json)

            #set up an array of aliases, letting the user know this is FOR REAL FOR REAL 
            aliases = []

            for names in load['Aliases']:    
                aliases.append(names['Name'])

            print(color.PURPLE + "Would delete:" + color.END)
            print(color.PURPLE + "Lambda: %s" % lambda_name + color.END)
            for item in aliases:
                print(color.PURPLE + "Alias: %s" % item + color.END)

            versions = client.list_versions_by_function(
                                    FunctionName='%s' % lambda_name,
                                )

            version_json = json.dumps(versions, indent=4)
            load_json = json.loads(version_json)
            versions = load_json['Versions']
            
            #set up an array of versions, letting the user know this is again, for really real
            avail_versions = []

            for version in versions:
                avail_versions.append(version['Version'])

            for vers in avail_versions:
                print(color.PURPLE + "Version: %s" % vers + color.END)
        except ClientError as error:
            print(color.RED + error.response['Error']['Message'] + color.END)
    else:
        #just to be extra cautious, let's double check with the user
        double_check = input("Are you SURE you want to delete this lambda (y/n)? ")
        lowered_checked = double_check.lower()

        #validate their answer then do the deed
        if lowered_checked == 'y':
            try:
                delete = client.delete_function(
                    FunctionName='%s' % lambda_name
                    )
                if check(lambda_name):
                    print(color.RED + "Failed to delete Lambda" + color.END)
                    return False
                else:
                    print(color.CYAN + "Lambda %s deleted successfully" % lambda_name + color.END)
                    return True
            except ClientError as error:
                print(color.RED + error.response['Error']['Message'] + color.END)
                sys.exit(1)
        else:
            print(color.RED + "Exiting" + color.END)
            sys.exit(1)
