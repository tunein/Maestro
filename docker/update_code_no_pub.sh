#!/bin/bash

#App stuff
lambda_name=%env.lambda_name%
environment=%env.environment%

######### LETS START! #############
docker run -e AWS_ACCESS_KEY_ID='%env.AWS_ACCESS_KEY_ID%' -e AWS_SECRET_ACCESS_KEY='%env.AWS_SECRET_ACCESS_KEY%' -e AWS_DEFAULT_REGION='%env.region%' -v `pwd`:/app tunein/maestro:0.1 update-code --no_pub $environment.$region.json
