#!/bin/bash

lambda_name=%env.lambda_name%

check_running=$(docker ps -f name=maestro-build-container-$lambda_name | grep Up | awk '{ print $1 }')
if [ $? -eq 1 ]; then
  echo "The container is still running.."
else
  docker rmi --force maestro-build-container-$lambda_name
fi