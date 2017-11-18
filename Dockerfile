from alpine:3.6

RUN apk add --update \
	python3 \
	python3-dev \
	&& pip3.6 install --upgrade pip \
	&& pip3.6 install boto3 \
	&& pip3.6 install awscli

WORKDIR /app

ADD . .

RUN pip3 install .

ENTRYPOINT ["maestro"]
CMD ["--help"]