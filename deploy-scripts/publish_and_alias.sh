#!/bin/bash

git_sha=$(git rev-parse HEAD)

docker run --rm -e AWS_ACCESS_KEY_ID='%env.AWS_ACCESS_KEY_ID%' -e AWS_SECRET_ACCESS_KEY='%env.AWS_SECRET_ACCESS_KEY%' -e AWS_DEFAULT_REGION='%env.region%' -v `pwd`:/app tunein/maestro-alpine:0.1.1 publish --version_description $git_sha %env.environment%.%env.region%.json

docker run --rm -e AWS_ACCESS_KEY_ID='%env.AWS_ACCESS_KEY_ID%' -e AWS_SECRET_ACCESS_KEY='%env.AWS_SECRET_ACCESS_KEY%' -e AWS_DEFAULT_REGION='%env.region%' -v `pwd`:/app tunein/maestro-alpine:0.1.1 create-alias --publish %env.environment%.%env.region%.json