FROM tunein/py36alpine:0.1

WORKDIR /app

ADD . .

RUN pip3 install .

ENTRYPOINT ["maestro"]
CMD ["--help"]