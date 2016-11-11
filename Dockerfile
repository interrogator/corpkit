FROM alpine:latest
MAINTAINER interro_gator

RUN apk add --update \
    python3 \
    python-dev \
    py-pip \
    build-base \
    git \
    libfreetype6-dev \
    libpng-devel

RUN apk --update add openjdk-8-jre

RUN pip install --upgrade pip

RUN rm -rf /var/cache/apk/*

RUN git clone https://github.com/interrogator/corpkit
RUN pip install -r corpkit/requirements.txt

RUN python -m corpkit.download.corenlp
CMD python -m corpkit.env
