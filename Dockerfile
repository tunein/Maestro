FROM tunein/python36builder:latest

WORKDIR /app

ADD . .

RUN pip3 install .

ENTRYPOINT ["maestro"]
CMD ["--help"]