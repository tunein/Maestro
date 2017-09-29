#!/bin/bash

maestro_token=%env.MAESTRO_GIT_TOKEN%
AWS_ACCESS_KEY_ID=%env.AWS_ACCESS_KEY_ID%
AWS_SECRET_ACCESS_KEY=%env.AWS_SECRET_ACCESS_KEY%
environment=%env.environment%
region=%env.region%


####
# VCS Shit

##Build dat shit
docker run -v `pwd`:/app -w /app/helloworld microsoft/dotnet dotnet restore && dotnet build -o bin

mkdir -p dist

cp /bin/*.dll /dist