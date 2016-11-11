FROM alpine:latest
MAINTAINER interro_gator

RUN apk add --update \
    python3 \
    python-dev \
    py-pip \
    build-base \
    git \
    libpng \
    freetype \
    pkgconf \
    libxft-dev \
    libxslt1-dev \
    libxml2-dev

RUN apk --update add openjdk8-jre-base

# needed for numpy
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

RUN pip install --upgrade pip
RUN pip install cython
RUN pip install numpy

RUN rm -rf /var/cache/apk/*

RUN git clone git://github.com/matplotlib/matplotlib.git
RUN cd matplotlib && python setup.py install && cd ..

RUN git clone https://github.com/interrogator/corpkit
RUN pip install -r corpkit/requirements.txt

RUN python -m corpkit.download.corenlp
CMD ["python","-m","corpkit.env"]
