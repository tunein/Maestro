-----------------------------------------------------------
     __	   __          ___      ______	______  _________  _______  ________
    /  \  /	 \        /   \    |  ____|| _____||___   ___||  ___  ||  ____  |
   / /\	\/ /\ \      / /_\ \   | |____ | |____     | |    | |___| || |    | |
  /	/  \__/	 \ \    / _____ \  |  ____||____  |    | |    |  _____|| |    | |
 / /          \ \  / /     \ \ | |____ 	____| |    | |    |	 ___  \| |____| |
/ /			   \ \/ /       \ \|______||______|    |_|    |_|   |_||________|

Created by M. Moon/We'reWolf Industries Copyright 2017<br>
-----------------------------------------------------------
Current State: v0.1<br>
<br>
-All actions work<br>
-Still working on packaging into a proper CLI tool<br>
<br>
-----------------------------------------------------------
Maestro is a command line tool for creating, updating, deleting, and publishing Lambdas for Amazon Web Services<br>
<br>
-It takes a json document as input to fill out all the information necessary for creating a lambda<br>
-In the directory you're working in it looks for a directory called "lambda" and packages the contents into a zip<br>
-Once complete it uploads your package into lambda with all of the settings you provided<br>
<br>
-----------------------------------------------------------
Required Packages..<br>
<br>
AWS CLI Tools/Boto3<br>
-----------------------------------------------------------
Steps will be...<br>
<br>
cd into function_name directory<br>
command: maestro create function_name.json<br>
<br>
At the moment it is only functioning in the directory where the application code lives<br>
<br>
-----------------------------------------------------------
Folder Hierarchy...<br>
<br>
/function_name<br>
---function_name.json<br>
---/lambda<br>
------function_name.py (or any other compatible language)<br>
------/dependency-1<br>
--------stuff.txt<br>
------/dependency-2<br>
------/dependency-etc<br>