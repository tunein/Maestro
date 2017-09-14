Created by M. Moon/Perilune Inc Copyright 2017<br>

<b>Current State: v0.1</b><br>
<br>
<b>Maestro is a command line tool for creating, updating, deleting, and publishing Lambdas for Amazon Web Services</b><br>
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
--publish<br>
	<i>Rolls over any manual input for "publish" options.<br>
	Currently only works with "create" and "update-code" functions</i><br>
--create_trigger<br>
--invoke_method <i>[s3, cloudwatch, sns]</i><br>
--invoke_source <i>name of your resource</i><br>
<br>
<i>It is also possible to string actions together</i><br>
Example 1:<br>
maestro update-code --alias dev --publish --create_trigger --invoke_method s3 --invoke_source maestro-test-trigger-dev example_template.json<br>
</i>This will:</i><br>
--publish updated code<br>
--reallocate the alias 'dev' to the new version<br>
--add "PUT" events for the s3 bucket 'maestro-test-trigger-dev' as the lambda invocator<br>
<br>
Example 2:<br>
maestro update-code --alias prod --publish example_template.json<br>
</i>This will:</i><br>
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
