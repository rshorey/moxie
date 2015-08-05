# VERSION   0.1
FROM        debian:jessie
MAINTAINER  Paul R. Tagliamonte <paultag@debian.org>

ENV DEBIAN_FRONTEND noninteractive

RUN echo "deb-src http://http.debian.net/debian/ jessie main" > /etc/apt/sources.list.d/moxie.list
RUN apt-get update && apt-get install -y \
    python3.4 \
    python3-pip \
    git \
    node-uglify \
    node-less \
    coffeescript \
    locales-all

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
ENV PYTHONIOENCODING utf-8

RUN apt-get update && apt-get build-dep -y python3-psycopg2 python3-cryptography

RUN mkdir -p /opt/pault.ag/
ADD . /opt/pault.ag/moxie/

RUN cd /opt/pault.ag/moxie; python3.4 /usr/bin/pip3 install \
    slacker websockets aiohttp
# Hurm. Why?

RUN cd /opt/pault.ag/moxie; python3.4 /usr/bin/pip3 install -r \
        requirements.txt

RUN python3.4 /usr/bin/pip3 install -e \
        /opt/pault.ag/moxie/

RUN make -C /opt/pault.ag/moxie/

RUN mkdir -p /moxie/
WORKDIR /moxie/

CMD ["moxied"]
