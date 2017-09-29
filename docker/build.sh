#!/bin/bash

##Build dat shit
docker run -v `pwd`:/app -w /app/helloworld --entrypoint /bin/bash microsoft/dotnet -c 'dotnet restore && dotnet build -o dist'