#!/bin/bash

##Build dat shit
docker run --rm -v `pwd`:/app -w /app/LogForwarder --entrypoint /bin/bash microsoft/dotnet -c 'dotnet restore && dotnet build --configuration Release -o dist'