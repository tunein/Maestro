#!/bin/bash

environment=%env.environment%
region=%env.region%
lambda_name=%env.lambda_name%
git_sha=$(git rev-parse HEAD)

publish_code () {
  check_images=$(docker images maestro-build-container-$lambda_name)
  if [ $? -eq 0 ]; then
    echo "Publishing version"
    docker run -e AWS_ACCESS_KEY_ID='%env.AWS_ACCESS_KEY_ID%' -e AWS_SECRET_ACCESS_KEY='%env.AWS_SECRET_ACCESS_KEY%' -e AWS_DEFAULT_REGION='%env.region%' -v `pwd`:/app maestro publish --version_description $git_sha $environment.$region.json
    true
  else
    echo "No container found"
    false
  fi
}

update_alias () {
  check_images=$(docker images maestro-build-container-$lambda_name)
  if [ $? -eq 0 ]; then
    echo "Updating alias"
    docker run -e AWS_ACCESS_KEY_ID='%env.AWS_ACCESS_KEY_ID%' -e AWS_SECRET_ACCESS_KEY='%env.AWS_SECRET_ACCESS_KEY%' -e AWS_DEFAULT_REGION='%env.region%' -v `pwd`:/app maestro update-alias --publish $environment.$region.json
    true
  else
    echo "No container found"
    false
  fi
}

if publish_code; then 
  update_alias
fi