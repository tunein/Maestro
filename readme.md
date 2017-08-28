     __	   __          ___      ______	______  _________  _______  ________
    /  \  /	 \        /   \    |  ____|| _____||___   ___||  ___  ||  ____  |
   / /\	\/ /\ \      / /_\ \   | |____ | |____     | |    | |___| || |    | |
  /	/  \__/	 \ \    / _____ \  |  ____||____  |    | |    |  _____|| |    | |
 / /          \ \  / /     \ \ | |____ 	____| |    | |    |	 ___  \| |____| |
/ /			   \ \/ /       \ \|______||______|    |_|    |_|   |_||________|

Created by M. Moon/We'reWolf Industries Copyright 2017
-----------------------------------------------------------
Current State: v0.1

-All actions work
-Still working on packaging into a proper CLI tool

-----------------------------------------------------------
Maestro is a command line tool for creating, updating, deleting, and publishing Lambdas for Amazon Web Services

-It takes a json document as input to fill out all the information necessary for creating a lambda
-In the directory you're working in it looks for a directory called "lambda" and packages the contents into a zip
-Once complete it uploads your package into lambda with all of the settings you provided

-----------------------------------------------------------
Required Packages..

AWS CLI Tools/Boto3
-----------------------------------------------------------
Steps will be...

cd into function_name directory
command: maestro create function_name.json

At the moment it is only functioning in the directory where the application code lives

-----------------------------------------------------------
Folder Hierarchy...

/function_name
---function_name.json
---/lambda
------function_name.py (or any other compatible language)
------/dependency-1
--------stuff.txt
------/dependency-2
------/dependency-etc