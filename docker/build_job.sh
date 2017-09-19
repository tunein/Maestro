#!/bin/bash

cd /Maestro/docker

maestro_token=%env.MAESTRO_GIT_TOKEN%
access_key=%env.AWS_ACCESS_KEY_ID%
secret_key=%env.AWS_SECRET_ACCESS_KEY%
region=$4
build_token=%env.APP_GIT_TOKEN%
user=$6
repo=$7
lambda_name=$8
environment=$9

docker build . -t maestro-build-container-$lambda_name \
        --build-arg maestro_token=$maestro_token \
        --build-arg access_key=$access_key \
        --build-arg secret_key=$secret_key \
        --build-arg region=$region \
        --build-arg build_token=$build_token \
        --build-arg user=$user \
        --build-arg repo=$repo \
        --build-arg lambda_name=$lambda_name \
        --build-arg enviro=$environment


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