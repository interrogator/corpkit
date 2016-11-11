FROM alpine:latest
MAINTAINER interro_gator

RUN apk add --update \
    python3 \
    python-dev \
    py-pip \
    build-base \

RUN apk --update add openjdk7-jre

RUN git clone https://github.com/interrogator/corpkit
RUN pip install -r corpkit/requirements.txt

CMD python -m corpkit.env
