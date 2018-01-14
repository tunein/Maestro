# Actions documentation

This section is the documentation for the actions of Maestro 

---

## Core actions

- create  
- update-code  
- update-config  
- publish  
- delete  
- create-alias  
- update-alias  
- delete-alias  
- invoke  
- init  
- import  

---

## How to use the 'create' action 

The create action is used to create a lambda, the first thing it does is checks to see if the lambda already exists in the specified account and region. If it doesn't, it creates the lambda!  

When using the `alias` field in your config file you can use the `--publish` command line flag to avoid being prompted to pick a version to assign to the alias. This will assign the alias to the $LATEST code. Useful for getting a lambda set up quickly.   

You can also use the `--dry_run` command to see if you have the valid permissions to create the lambda and see the output of what would have happened, before you run it for real.  

Example commands:  
`maestro create example.json`  
`maestro create --publish example.json`  
`maestro create --dry_run example.json`  

---

## How to use the 'update-code' action  

The update-code action is used to update the lambda code, there are a few command line flags that work with this action.

--no_pub flag:  
The most general use of this action is to push your updated code to $LATEST (while your production traffic hits an alias). This is done by running `maestro update-code --no_pub example.json`. Using the `--no_pub` flag does NOT publish a new version of the code, keeping your versioning clean and to the point. When you've tested and are ready to publish you can use the 'publish' action (see below for usage).  

--publish flag:
Another common use of this action is to update the code (say you've already tested it extensively) and automatically publish a new version of it. AWS handles assigning version numbers.  


Example commands:  
`maestro update-code --no_pub example.json`  
`maestro update-code --publish example.json`  
`maestro update-code --publish --alias dev example.json`  

---

## How to use the 'update-config' action  

The update-config action is used to update the lambda configuration. This action does not have any available command line flags.  

The most common use case of this action is to update your lambda configuration (VPC, tags, variables, DLQ, trigger) before pushing a code update. It allows you to change virtually every configuration setting, as if you were creating a lambda from scratch, except for the code.  

If they are not specified in the config file you can use the `--create_trigger` or `--delete_trigger` to either create or delete a trigger. If you're using the `--create_trigger` you must specify `--invoke_method` and `--invoke_source` to specify the method and source for the trigger.  

If you are addressing your triggers in your config file those triggers will be used over the triggers specified in the config file.  

Example commands:  
`maestro update-config example.json`  
`maestro update-config --create_trigger --invoke_method s3 --invoke_source bucket_name`  

---

## How to use the 'publish' action  

The publish action is used to publish a new version of a lambda. 

The most common use case of thise action is to publish a version of your code, after validating that it is working well on $LATEST.

Example commands:  
`maestro publish example.json`

---

## How to use the 'delete' action  

The delete action used to delete your lambda. It handles deleting the lambda only, not unsubscribing topics. It prompts you to ensure you REALLY want to delete your lambda.

Example commands:  
`maestro delete example.json`

---

## How to use the 'create-alias' action

This is used to create a new alias for your lambda, without specifying it in your config file. It should be remembered that if an alias exists in your config file that will be used over an alias specified in the CLI. When first creating your lambda you should decide if you are going to use one, or multiple aliases and decide whether to use the config file or the 'create-alias' action to create aliases. 

Example commands:  
`maestro create-alias --alias dev example.json`

In this command the alias we're creating is 'dev'. You are free to call your aliases whatever you like.

---

## How to use the 'update-alias' action  

This is used to update the alias specified in either the config file or from the CLI. It should be remembered that if an alias exists in your config file that will be used over an alias specified in the CLI.  

The most common use case of this is updating your alias to a newly published version (from the 'publish' action)  

Example commands:  
`maestro update-alias example.json`  
`maestro update-alias --alias dev example.json`  

In the second command we're updating the alias 'dev'. The alias MUST exist. 

---

## How to use the 'delete-alias' action  

This is used to delete the alias specified in either the config file or from the CLI. It should be remembered that if an alias exists in your config file that will be used over an alias specified in the CLI.  

This isn't used very often, but is useful if you've created a new alias to test a breaking change, then need to drop it.  

Example commands:  
`maestro delete-alias example.json`  
`maestro delete-alias --alias dev example.json`  

---

## How to use the 'invoke' action  

This is used to test invoke the code.  

You can pass a payload using the `--payload` flag, pass an alias using the `--alias` flag, and an invoke type using the `--invoke_type`. Invoke types are Event, RequestResponse, and DryRun.    

If 'alias' exists in the 'initializers' section of your config file that alias will be used over the alias specified in the CLI.  

Example commands:  
`maestro invoke example_template.json`  
`maestro invoke example_template.json --payload test_payload.json --alias dev --invoke_type RequestResponse`  

--- 

## How to use the 'init' action  

This action is used to help users create a config file without having to go through the hassle of creating a json config file themselves. It uses the filename specified in the CLI as the name of the config file and walks the user through all the steps necessary to create a config file in your PWD.

Example commands:  
`maestro init example.json`  

The above command will create `example.json` in your PWD.  

---

## How to use the 'import' action

This action is used to import an existing lambda into being managed by Maestro/as infrastructure as code. When running this command you are prompted for the name of the lambda and if you'd like to import the configuration of a specific alias. Maestro checks to see if your lambda and alias exists then writes your configuration file for you. To kick off the command, first decide what you want to name your file then run the example command.

Example commands:  
`maestro import example.json`  

The above command will create `example.json` in your PWD and dump the lambda's configuration into it.  