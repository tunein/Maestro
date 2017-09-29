#!/bin/bash

aws s3 cp s3://ti-devops-test-dockerfiles/Maestro/Dockerfile.gocompile

build () {
if [ -f Dockerfile ]; then
    docker build -f Dockerfile.gocompile . -t go-build-container-$lambda_name \
            --build-arg maestro_token=$maestro_token \
            --build-arg access_key=$AWS_ACCESS_KEY_ID \
            --build-arg secret_key=$AWS_SECRET_ACCESS_KEY \
            --build-arg region=$region \
            --build-arg app=$app
    true
else
    echo "No build file found"
    false
fi
}

run () {
check_images=$(docker images maestro-build-container-$lambda_name)
if [ $? -eq 0 ]; then
  docker run go-build-container-$lambda_name
  true
else
  echo "false"
  false
fi
}

remove () {
check_running=$(docker ps -f name=go-build-container-$lambda_name | grep Up | awk '{ print $1 }')
if [ $? -eq 1 ]; then
  echo "The container is still running.."
else
  docker rmi --force go-build-container-$lambda_name
  true
fi
}

if build; then
  if run; then
    remove
fi