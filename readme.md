# Maestro 

Created by M. Moon/Perilune Inc Copyright 2017  

![](http://pixel.nymag.com/imgs/daily/vulture/2015/gifs/epic-conductor-valery-gergiev.w529.h352.gif)  

Current State: v0.1.4

***Maestro is a command line tool for managing Lambdas for Amazon Web Services***  
- It takes a json document as an input to fill out all the information necessary for creating a lambda  
- In the directory you're working in it looks for a directory called "lambda" and packages the contents into a zip  
- Once complete it uploads your package into lambda with all of the settings you provided  

---

**To install**  
- Clone this directory  
- CD into the main directory containing setup.py  
- Issue the following command: "pip install ."  

**Required Packages**  
- python 3.*  
- pip  
- AWS CLI Tools  
- Boto3  

---

**Current Core Available actions**  
- maestro create function_name.json  
- maestro update-code function_name.json  
- maestro update-config function_name.json  
- maestro publish function_name.json  
- maestro delete function_name.json  
- maestro create-alias function_name.json  
- maestro update-alias function_name.json  
- maestro delete-alias function_name.json  
- maestro invoke function_name.json  
- maestro init function_name.json


---

**Command line flags**  
- --publish *autopasses for publish input args on 'create' and 'update-code' actions*  
- --create_trigger *stores 'True', must be used to create trigger, must include invoke method and source*  
- --invoke_method *$[s3, cloudwatch, sns])*  
- --invoke_source *$name of your resource*  
- --dry_run *dry run*  
- --version *specify a specific version, this is used for invoking lambdas*  
- --invoke_type *specify an invocation type from the CLI, options are: RequestResponse, Event, and DryRun)*  
- --payload *used to specify a file with a json payload to pass into the lambda, used to test invoking*  
- --no_pub *this is used to automatically pass over the "would you like to publish?" input stage for code updates. Useful for pushing code up to $LATEST and testing without mucking with aliases/versions*  
- --event_type *this is used for the 'S3' invoke_method only, and allows you to use "ObjectCreated" and "ObjectRemoved" for the event type to invoke your lambda, default is "ObjectCreated"*  
- --version_description *this is used for the "publish" action to pass a version description in, default is current date/time in UTC*  

---

**It is also possible to string actions together**  

Example 1:  
 - maestro update-code --alias dev --publish --create_trigger --invoke_method s3 --invoke_source maestro-test-trigger-dev example_template.json  

This will:  
- publish updated code  
- reallocate the alias 'dev' to the new version  
- add "PUT" events for the s3 bucket 'maestro-test-trigger-dev' as the lambda invocator  

-

Example 2:   
- maestro update-code --alias prod --publish example_template.json  

This will:   
- Publish a new version of your lambda and then assign it the alias of "prod"  

---
**Notes**  
  
#### "--dry-run" is vailable on the following Actions:
- create  
- update-code  
- delete  
- create-alias  
- update-alias  
- delete-alias  
- create-trigger (and by proxy: invoke_method & invoke_source)  


#### Action "invoke" specific notes: 

Example 1:  
- maestro invoke example_template.json  

This will:  
- Return a list of available aliases to invoke, prompt the user to pick one  
- Prompt the user for an invocation type (Event, RequestResponse, DryRun)  
- Ask for a payload file (it expects that the file is in the current working directory)  
- Invoke!  
- Presently only 'RequestResponse' returns logs to the console  

Example 2:  
- maestro invoke example_template.json --payload test_payload.json --alias dev --invoke_type RequestResponse  

This will:  
- Do everything stated above without user prompts

#### Action "init" specific notes:  

Running "maestro init yourfilename.json" will do the following:  
- Walks you through all the steps of creating a config file 
- Uses filename argument to name file  
- Puts a json configuration document in a file in your PWD  

----
**Usage**

To use:  
- cd into the directory where your code is:
- command: maestro create function_name.json

Folder Hierarchy:  

/function_name  
---function_name.json  
---/dist
------function_name.py (or any other compatible language)  
------/dependency-1  
--------stuff.txt  
------/dependency-2  
------/dependency-etc  

Notes:  
- The expectation of Maestro is that your code (or binary) and all necessary libs are in a folder called "dist" that is at the same directory level as your configuration file. THIS IS A MUST.

---  

**Docker**

Usage of docker is recommended for use in CICD pipelines to reduce dependency management on build agents  

- Example  

docker run --rm -e AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id) -e AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key) -e AWS_DEFAULT_REGION=$YOURREGION -v `pwd`:/app maestro-builder $YOURACTION $YOURFILENAME.json  

Example notes:  
- I've tagged the container "maestro-builder" (docker build -t maestro-builder . from the repo's root directory)  
- I'm using 'aws configure get', to fill in the keys, you can replace this directly with your keys  
- I've replaced the default region with 'YOURREGION', place a valid region (ie: us-west-2) in place of this  
- I'm mount my $PWD to the /app directory of the container (your /dist folder and config file should be at this level)  
- Actions and config file name come AFTER the container name (maestro is the entrypoint, you don't need to specify that)  

---

**Current roadmap:**  
- Add API Gateway trigger Support  
- Add IoT Trigger Support  
- Add CodeCommit Trigger Support  
- Add Cognito Sync Trigger Support  
