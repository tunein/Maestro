FROM centos:latest
MAINTAINER M.Moon

ARG TOKEN

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

##Get the application
RUN git clone https://$TOKEN:x-oauth-basic@github.com/MoonMoon1919/Maestro.git

##Install the app
WORKDIR Maestro
RUN pip3 install .
#RUN pip3 install -r requirements.txt
RUN pip3 install boto3