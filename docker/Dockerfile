FROM centos:latest
MAINTAINER M.Moon

ARG maestro_token
ARG access_key
ARG secret_key
ARG region

ARG build_token
ARG user
ARG repo
ARG lambda_name

##Prep the system & get the basics
RUN yum update -y \
  && yum groupinstall -y "Development Tools" \
  && yum groupinstall -y development \
  && yum install -y \
    epel-release \
    zip \
    openssl \
    wget \
    yum-utils \
    git 

##Get python and all the goodies
RUN yum install -y \
	https://centos7.iuscommunity.org/ius-release.rpm \
	&& yum install -y \
	python36u \
	python36u-pip \
	python36u-devel \
	python36u--setuptools \
	&& easy_install-3.6 pip

##Get AWS CLI
RUN curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip"
RUN unzip awscli-bundle.zip
RUN ./awscli-bundle/install -b ~/bin/aws

RUN mkdir ~/.aws && touch ~/.aws/config && touch ~/.aws/credentials
RUN echo -en "[default]\nregion = $region" >> ~/.aws/config
RUN echo -en "[default]\naws_access_key_id = $access_key\naws_secret_access_key = $secret_key" >> ~/.aws/credentials

WORKDIR /home

##Get the application
RUN git clone https://$maestro_token:x-oauth-basic@github.com/MoonMoon1919/Maestro.git

##Install the app
WORKDIR Maestro
RUN pip3 install .
#RUN pip3 install -r requirements.txt
RUN pip3 install boto3

WORKDIR /home
######################Application Portion#################

RUN git clone https://$build_token:x-oauth-basic@github.com/$user/$repo.git

WORKDIR $repo

CMD maestro create $lambda_name.json