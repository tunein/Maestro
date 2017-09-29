#!/bin/bash

aws s3 cp s3://ti-devops-test-dockerfiles/Maestro/Dockerfile.gocompile

if [ -f Dockerfile ]; then
    docker build -f Dockerfile.gocompile . -t go-build-container-$lambda_name \
            --build-arg maestro_token=$maestro_token \
            --build-arg access_key=$AWS_ACCESS_KEY_ID \
            --build-arg secret_key=$AWS_SECRET_ACCESS_KEY \
            --build-arg region=$region \
            --build-arg app=$app
else
    echo "No build file found"
fi

check_running=$(docker ps -f name=go-build-container-$lambda_name | grep Up | awk '{ print $1 }')
if [ $? -eq 1 ]; then
  echo "The container is still running.."
else
  docker rmi --force go-build-container-$lambda_name
fi