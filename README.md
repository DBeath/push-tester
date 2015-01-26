PuSH-Tester
===========

PubSubHubbub publisher testing application. Designed to allow the creation of [RSS](http://en.wikipedia.org/wiki/RSS) feeds for testing [PubSubHubbub](https://code.google.com/p/pubsubhubbub/) Hubs and Subscribers.

#Installation

Install PostgreSQL

	sudo apt-get install postgresql-9.4 postgresql-server-dev-9.4 postgresql-contrib

Install Python

	sudo apt-get install python python-dev python-pip libpq-dev python-psycopg2

##Create PostgreSQL user and database
Log into Postgres

	sudo -u postgres psql postgres
	
Create user and database

	postgres=# CREATE USER pushtesteruser WITH PASSWORD 'password';

	postgres=# CREATE DATABASE pushtesterdb;

	postgres=# GRANT ALL PRIVILEGES ON DATABASE pushtesterdb TO pushtesteruser;

##PuSH-Tester setup
Clone this repository

	git clone https://github.com/DBeath/push-tester.git

Install and activate Virtualenv

	sudo pip install virtualenv

	virtualenv env

	source env/bin/activate

Install dependencies

	pip install -r requirements.txt

Create a folder called ```instance```. Create a ```config.py``` file in the instance folder and override all applicable settings. 

Set up the database

	python run.py db upgrade

To create admin users, run the following command

	python run.py add_admin *admin_email* *admin_password*

##Run PuSH-Tester
####Development

	python run.py runserver

####Production with uWSGI and Nginx
Install Nginx and uWSGI

	sudo apt-get install nginx uwsgi

Modify the ```nginx.conf``` file from the deployments folder and copy it to ```/etc/nginx/sites-enabled```. 

Reload Nginx

	sudo service nginx reload

Modify the ```uwsgi.ini``` file from the deployments folder and copy it the root folder for PuSH-Tester.

Run the application with

	env/bin/uwsgi uwsgi.ini
