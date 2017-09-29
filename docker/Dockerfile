FROM tunein/python36builder:latest

ARG maestro_token
ARG access_key
ARG secret_key
ARG region

ARG app

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

COPY $app /tmp/$app

WORKDIR /tmp/$app

ENTRYPOINT ["maestro"]
CMD ["--help"]