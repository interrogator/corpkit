FROM alpine:latest
MAINTAINER interro_gator

# set up a workspace so we can cache python stuff
RUN rm -rf /.src && mkdir /.src
COPY requirements.txt /.src/requirements.txt

# add corenlp
# COPY ~/corenlp /.src

# use the workspace for everything
WORKDIR /.src

# install the basics
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
    libxml2-dev \
    readline

# install java for parsing
RUN apk --update add openjdk8-jre-base

# needed for numpy
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
RUN ln -s /usr/include/libxml2/libxml/xmlversion.h /usr/include/xmlversion.h
RUN mkdir /usr/include/libxml
RUN ln -s /usr/include/libxml2/libxml/xmlversion.h /usr/include/libxml/xmlversion.h
RUN ln -s /usr/include/libxml2/libxml/xmlexports.h /usr/include/xmlexports.h
RUN ln -s /usr/include/libxml2/libxml/xmlexports.h /usr/include/libxml/xmlexports.h

# stop pip from complaining
RUN pip install --upgrade pip

# python heavyweight stuff
RUN pip install cython
RUN pip install numpy
RUN pip install colorama

# remove old stuff --- not sure it does much
RUN rm -rf /var/cache/apk/*

# get matplotlib github version
RUN git clone git://github.com/matplotlib/matplotlib.git
RUN cd matplotlib && python setup.py install && cd ..

# install corpkit requirements
RUN pip install -r requirements.txt

RUN pip install docker-py

# add everything from corpkit to working dir
COPY . /.src

# install corpkit itself
RUN python /.src/setup.py install

# download might be needed for licence issues
#RUN python -m corpkit.download.corenlp /

CMD python -m corpkit.env docker=corpkit

WORKDIR /projects

