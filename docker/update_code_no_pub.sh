#!/bin/bash

#App stuff
lambda_name=%env.lambda_name%
environment=%env.environment%

######### LETS START! #############
check_images=$(docker images maestro-build-container-$lambda_name)
if [ $? -eq 0 ]; then
  docker run -e AWS_ACCESS_KEY_ID='%env.AWS_ACCESS_KEY_ID%' -e AWS_SECRET_ACCESS_KEY='%env.AWS_SECRET_ACCESS_KEY%' -e AWS_DEFAULT_REGION='%env.region%' -v `pwd`:/app maestro update-code --no_pub $environment.$region.json
else
  echo "false"
fi