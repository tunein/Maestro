#External libs
import boto3
import sys
import json
import os
import datetime
from botocore.exceptions import ClientError

#Our modules
import maestro.lambda_config as lambda_config

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
s3 = boto3.resource('s3')
client = boto3.client('s3')

#Establish easy to read variables for stuff from config file
ACCEPTED_PROMPT_ACTIONS = lambda_config.ACCEPTED_PROMPT_ACTIONS
REGIONS = lambda_config.REGIONS
ACL_ANSWERS = lambda_config.ACL_ANSWERS

def check_file(lambda_name):
    '''
    Checks to make sure the archive exists, this is used as part of the upload function to make sure
    it's trying to upload a real file.

    args:
        lambda_name: the name of the lambda (this is what the archive is saved as), retrieved from the config file
    '''
    file_path = os.getcwd() + '/%s.zip' % lambda_name
    if os.path.exists(file_path):
        return True
    return False

def check_s3(bucket_name):
    '''
    Checks to make sure the specified s3 bucket exists, if it does not user is sent to the 'create_bucket' function

    args:
        bucket_name: name of the s3 bucket, retrieved from config file
    '''
    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError:
        prompt = input("Bucket '%s' does not exist would you like to create? 'y/n': " % bucket_name)
        if prompt in accepted_prompt_actions:
            if prompt == 'y':
                if create_bucket():
                    return True
            else:
                print("Exiting...")
                return False
        
def create_bucket(bucket_name):
    '''
    This function exists as a helper to users, if they want to specify a bucket that doesn't exist yet
    that is perfectly acceptible, this function will run if that is the case and do the setup

    args:
        bucket_name: name of the bucket to create
    '''
    acl = input("Give your bucket an ACL (Accepted answers: 'private', 'public-read', 'public-read-write', 'authenticated-read'): ")
    
    if acl in ACL_ANSWERS:
        bucket_location = input("What region would you like to put the bucket in? ")
        if bucket_location.lower() in REGIONS:
            role = json_parser()["initializers"]["role"]

            create = client.create_bucket(
                ACL=acl,
                Bucket='%s' % bucket_name,
                CreateBucketConfiguration={
                        'LocationConstraint': '%s' % bucket_location
                }
            )
            return True
            print("Creating bucket")
        print("Invalid region")
        return False
    print("Invalid ACL")
    return False

def upload_file(lambda_name, bucket_name, dry_run=False):
    '''
    Performs the upload action for the zip'd archive

    args:
        lambda_name: name of the lambda/archive file, pulled from config file
        bucket_name: name of the s3 bucket, pulled from config file
    '''
    file = os.getcwd() + '/%s.zip' % lambda_name
    filename = '%s.zip' % lambda_name
    if check_file(lambda_name):
        if dry_run:
            print(color.PURPLE + "***Dry Run enabled, would have uploaded backup archive to S3 bucket %s***" % bucket_name + color.END)
            return True
        else:
            upload = s3.Bucket(bucket_name).upload_file(file, filename)
            print("Uploading file to S3")
            return True
    else:
        print("Hmm... I couldn't find the file")
        return False

def check_upload_exists(lambda_name, bucket_name, dry_run=False):
    '''
    Checks to see if the backup object exists in s3 after upload is completed

    args:
        lambda_name: name of the lambda/archive file, pulled from config file
        bucket_name: name of the s3 bucket, pulled from config file
    '''
    filename = '/%s.zip' % lambda_name

    if dry_run:
        return True
    else:
        try:
            file = s3.Object(bucket_name, filename)
            if file.key == filename:
                print("File %s exists in %s" % (filename, bucket_name))
                return True
            else:
                print("No file found in %s" % bucket_name)
                return False
        except ClientError as error:
            print(error.response['Error']['Message'])

########## Main Entrypoint ############
def main(lambda_name, bucket_name, dry_run):
    '''
    To simplify usage of this module as a whole this is the main entrypoint of the module
    
    args:
        lambda_name: name of the lambda, retrieved from config file
        bucket_name: name of the s3 bucket, retrieved from the confile file
    '''
    if check_s3(bucket_name):
        if upload_file(lambda_name, bucket_name, dry_run):
            if check_upload_exists(lambda_name, bucket_name, dry_run):
                return True