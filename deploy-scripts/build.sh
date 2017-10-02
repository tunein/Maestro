#!/bin/bash

##Build dat shit
docker run --rm -v `pwd`:/app -w /app/LogForwarder --entrypoint /bin/bash microsoft/dotnet -c 'dotnet publish --configuration Release -o dist'