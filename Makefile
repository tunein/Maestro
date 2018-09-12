SHELL := /bin/bash

AWS_ACCESS_KEY_ID := $(AWS_ACCESS_KEY_ID)
AWS_SECRET_ACCESS_KEY := $(AWS_SECRET_ACCESS_KEY)
S3_BUILD_BUCKET := $(S3_BUILD_BUCKET)
AWS_DEFAULT_REGION := $(AWS_DEFAULT_REGION)
MAESTRO_BUILDER_VERSION ?= 0.1.7
JFROG_REPO := tuneinartifactory-golden-images.jfrog.io

#--------------------------------------------------------------
# DOCKER MAESTRO
#--------------------------------------------------------------

build.maestro.builder:
	docker build -t $(JFROG_REPO)/maestro-alpine:$(MAESTRO_BUILDER_VERSION) -f ./Dockerfile . && \
	docker push $(JFROG_REPO)/maestro-alpine:$(MAESTRO_BUILDER_VERSION)

build.maestro.builder.test:
	docker build -t $(JFROG_REPO)/maestro-alpine:$(MAESTRO_BUILDER_VERSION) -f ./Dockerfile .