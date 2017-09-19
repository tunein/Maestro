FROM tunein/python36builder:latest

ARG maestro_token
ARG access_key
ARG secret_key
ARG region
ARG build_token
ARG user
ARG repo
ARG lambda_name
ARG enviro

RUN mkdir ~/.aws && touch ~/.aws/config && touch ~/.aws/credentials
RUN echo -en "[default]\nregion = $region" >> ~/.aws/config
RUN echo -en "[default]\naws_access_key_id = $access_key\naws_secret_access_key = $secret_key" >> ~/.aws/credentials

WORKDIR /home

##Get the application
RUN git clone https://$maestro_token:x-oauth-basic@github.com/MoonMoon1919/Maestro.git

##Install the app
WORKDIR Maestro
RUN pip3 install .

WORKDIR /home
######################Application Portion#################

RUN git clone https://$build_token:x-oauth-basic@github.com/$user/$repo.git

WORKDIR $repo

ENV name $lambda_name
ENV environment $enviro

ENTRYPOINT maestro update-code --alias $environment --publish $name.json