#!/bin/bash

#Maestro stuff
maestro_token=%env.MAESTRO_GIT_TOKEN%
maestro_repo=Maestro
maestro_user=MoonMoon1919

#AWS stuff
AWS_ACCESS_KEY_ID=%env.AWS_ACCESS_KEY_ID%
AWS_SECRET_ACCESS_KEY=%env.AWS_SECRET_ACCESS_KEY%
environment=%env.environment%
region=%env.region%

#App stuff
app=%env.APP_NAME%
lambda_name=%env.lambda_name%

mkdir -p app

######### LETS START! #############
##Grab the packaged code
aws s3 cp s3://ti-devops-lambda-files/$lambda_name/app/*  /app

##Get the deploy file
aws s3 cp s3://ti-devops-test-dockerfiles/Maestro/Dockerfile

if [ -f Dockerfile ]; then
    docker build . -t maestro-build-container-$lambda_name \
            --build-arg maestro_token=$maestro_token \
            --build-arg access_key=$AWS_ACCESS_KEY_ID \
            --build-arg secret_key=$AWS_SECRET_ACCESS_KEY \
            --build-arg region=$region \
            --build-arg app=$app
else
    echo "No build file found"
fi

check_images=$(docker images maestro-build-container-$lambda_name)
if [ $? -eq 0 ]; then
  docker run maestro-build-container-$lambda_name --update_code --no_pub $environment.$region.json
else
  echo "false"
fi