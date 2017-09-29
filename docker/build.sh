#!/bin/bash

maestro_token=%env.MAESTRO_GIT_TOKEN%
AWS_ACCESS_KEY_ID=%env.AWS_ACCESS_KEY_ID%
AWS_SECRET_ACCESS_KEY=%env.AWS_SECRET_ACCESS_KEY%
environment=%env.environment%
region=%env.region%

git clone https://$maestro_token:x-oauth-basic@github.com/MoonMoon1919/Maestro.git

cp Maestro/docker/Dockerfile .

cp Maestro/docker/Dockerfile.pypy .

build () {
if [ -f Dockerfile.pypy ]; then
    docker build -f Dockerfile.pypy . -t pypy-build-container-$lambda_name \
            --build-arg maestro_token=$maestro_token \
            --build-arg access_key=$AWS_ACCESS_KEY_ID \
            --build-arg secret_key=$AWS_SECRET_ACCESS_KEY \
            --build-arg region=$region
    true
else
    echo "No build file found"
    false
fi
}

run () {
check_images=$(docker images pypy-build-container-$lambda_name)
if [ $? -eq 0 ]; then
  docker run pypy-build-container-$lambda_name
  true
else
  echo "false"
  false
fi
}

remove () {
check_running=$(docker ps -f name=pypy-build-container-$lambda_name | grep Up | awk '{ print $1 }')
if [ $? -eq 1 ]; then
  echo "The container is still running.."
else
  docker rmi --force pypy-build-container-$lambda_name
  true
fi
}

if build; then
  if run; then
    remove
fi