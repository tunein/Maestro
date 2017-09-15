Created by M. Moon/Perilune Inc Copyright 2017<br>
<br>
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Maestro_2016.svg/500px-Maestro_2016.svg.png">
<br>
<b>Current State: v0.1</b><br>
<br>
<b>Maestro is a command line tool for managing Lambdas for Amazon Web Services</b><br>
<br>
-It takes a json document as an input to fill out all the information necessary for creating a lambda<br>
-In the directory you're working in it looks for a directory called "lambda" and packages the contents into a zip<br>
-Once complete it uploads your package into lambda with all of the settings you provided<br>
<br>
<b>To install:</b><br>
-Clone this directory<br>
-CD into the main directory containing setup.py<br>
-Issue the following command: "pip install ."<br>
<br>
<b>Required Packages..</b><br>
-python 3.*<br>
-pip<br>
-AWS CLI Tools<br>
-Boto3<br>
<br>
<b>Current Core Available actions</b><br>
maestro create function_name.json<br>
maestro update-code function_name.json<br>
maestro update-config function_name.json<br>
maestro publish function_name.json<br>
maestro delete function_name.json<br>
maestro create-alias --alias dev function_name.json<br>
maestro update-alias --alias dev function_name.json<br>
maestro delete-alias function_name.json<br>
<br>
<b>Command line flags</b><br>
--publish <i>autopasses for publish input args on 'create' and 'update-code' actions</i><br>
--create_trigger<br>
--invoke_method <i>$[s3, cloudwatch, sns])</i><br>
--invoke_source <i>$name of your resource</i><br>
<br>
<i>It is also possible to string actions together</i><br>
<b>Example 1:</b><br>
maestro update-code --alias dev --publish --create_trigger --invoke_method s3 --invoke_source maestro-test-trigger-dev example_template.json<br>
<br>
<i><u>This will</u>:</i><br>
--publish updated code<br>
--reallocate the alias 'dev' to the new version<br>
--add "PUT" events for the s3 bucket 'maestro-test-trigger-dev' as the lambda invocator<br>
<br>
<b>Example 2:</b><br>
maestro update-code --alias prod --publish example_template.json<br>
<br>
<i><u>This will</u>:</i><br>
Publish a new version of your lambda and then assign it the alias of "prod"<br>
<br>
<br>
<b>To use:</b><br>
cd into the directory where your code is:<br>
command: maestro create function_name.json<br>
<br>
<b>Folder Hierarchy...</b><br>
<br>
/function_name<br>
---function_name.json<br>
---/lambda<br>
------function_name.py (or any other compatible language)<br>
------/dependency-1<br>
--------stuff.txt<br>
------/dependency-2<br>
------/dependency-etc<br>
<br>
<br>
Current roadmap:<br>
-Add API Gateway integration and command line flags<br>
-Add letsencrypt/certbot integration for https<br>
-Add route53 integration for dns<br>
-Add in support for Event Source Mapping to work with DynamoDB and Kinesis Stream<br>
-Add "test invoke" action and pipe lambda logs back<br>
-Add dry run command line arg, add to all actions<br>
-Version deletion (automatically & intelligently)<br>
<br>
Current known issues:<br>
-If you try to re-add or change an invocation source to an alias after it's created it will return an error<br>
----<i>For re-adding this is the expected behavior but an unfriendly user experience<br>
    it needs to recognize the == and move on</i><br>
<br>
----<i>For changing sources I need to move the statement-ID to a command line arg<br>
    by doing so this will make deleting the source a manual step (from the CLI still)</i><br>
<br>
----<i>Since this is the last action run and does not impact code updates or changes<br>
    but will return an error saying the statement id already exists</i>
