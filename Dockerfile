FROM ubuntu:15.04

MAINTAINER David Beath <davidgbeath@gmail.com>

RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-9.4 \
    python \
    python-dev \
    libpq-dev \
    python-psycopg2 \
    python-setuptools \
    python-pip \
    nginx \
    supervisor \
    rsyslog

COPY requirements.txt /code/
WORKDIR /code/

RUN pip install -r requirements.txt

COPY . /code/

RUN echo "\ndaemon off;" >> /etc/nginx/nginx.conf
RUN rm /etc/nginx/sites-enabled/default

RUN ln -s /code/deployment/nginx.conf /etc/nginx/sites-enabled/
RUN ln -s /code/deployment/supervisor.conf /etc/supervisor/conf.d/

ENV ENV=production

EXPOSE 80

CMD ["supervisord", "-n"]