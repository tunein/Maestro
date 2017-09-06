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
<b>Current Available actions</b><br>
maestro create function_name.json<br>
maestro update-code function_name.json<br>
maestro update-config function_name.json<br>
maestro publish function_name.json<br>
maestro delete function_name.json<br>
maestro create-alias function_name.json<br>
maestro update-alias function_name.json<br>
maestro delete-alias function_name.json<br>
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
