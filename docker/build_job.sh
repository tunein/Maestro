#!/bin/bash

#Maestro stuff
maestro_token=%env.MAESTRO_GIT_TOKEN%
maestro_repo=Maestro
maestro_user=MoonMoon1919

#AWS stuff
access_key=%env.AWS_ACCESS_KEY_ID%
secret_key=%env.AWS_SECRET_ACCESS_KEY%
region=us-west-2

#App stuff
build_token=%env.APP_GIT_TOKEN%
user=MoonMoon1919
repo=maestro_lambda
lambda_name=maestro
environment=prod

if [ ! -d $maestro_repo ]; then
    git clone https://$maestro_token:x-oauth-basic@github.com/$maestro_user/$maestro_repo.git --branch master
else
    cd $maestro_repo && git pull origin
fi

cd ..

if [ -d $maestro_repo/docker ]; then
    cd $maestro_repo/docker && docker build . -t maestro-build-container-$lambda_name \
            --build-arg maestro_token=$maestro_token \
            --build-arg access_key=$access_key \
            --build-arg secret_key=$secret_key \
            --build-arg region=$region \
            --build-arg build_token=$build_token \
            --build-arg user=$user \
            --build-arg repo=$repo \
            --build-arg lambda_name=$lambda_name \
            --build-arg enviro=$environment
else
    echo "No directory found"
fi

cd ../..

check_images=$(docker images maestro-build-container-$lambda_name)
if [ $? -eq 0 ]; then
  docker run maestro-build-container-$lambda_name
else
  echo "false"
fi

check_running=$(docker ps -f name=maestro-build-container-$lambda_name | grep Up | awk '{ print $1 }')
if [ $? -eq 1 ]; then
  echo "The container is still running.."
else
  docker rmi --force maestro-build-container-$lambda_name
fi