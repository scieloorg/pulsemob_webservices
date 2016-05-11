# SciELO Pulsemob Webservices

This application implements webservices to acquire and make available Article data from SciELO database.

## Environment installation for CentOS 7

### 1. Install pre-requisites:

```sh
$ yum -y install libmemcached-devel
$ yum -y install git
$ yum -y install gcc
$ yum -y install python-devel postgresql-devel
$ yum -y install zlib-devel
$ yum install libjpeg-devel
$ yum -y install libffi-devel
$ yum -y -y install openssl-devel
$ yum -y install nodejs
$ yum install vim
$ easy_install pip
$ pip install virtualenv
```

### 2. Install and configure Solr:

To install and configure Solr, [see here](https://github.com/Infobase/pulsemob_solr).

### 3. Install the database:

To install PostgreSQL, [see here](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-centos-7).

Once it's installed, create database and user. Later on you'll need database name, user and password information.
```sh
$ su postgres
$ createdb pulsemob_db
$ psql pulsemob_db
$ CREATE USER your_user_name WITH PASSWORD 'your_password';
```

### 4. Install and configure Nginx
To install Nginx, [see here](https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-centos-7).

For appropriate settings, add [this file](https://github.com/Infobase/pulsemob_webservices/blob/master/configuration/nginx/conf.d/pulsemob.conf) to path */etc/nginx/conf.d/* and replace */etc/nginx/nginx.conf* for [this file](https://github.com/Infobase/pulsemob_webservices/blob/master/configuration/nginx/nginx.conf).

## Checking out source code, setting and running
### 1. Use virtualenv to create an application environment and activate it:

```sh
$ virtualenv --distribute --no-site-packages -p python2.7 scielopulsemob-env
$ source scielopulsemob-env/bin/activate
```
### 2. Go to a suitable installation directory and checkout the scielopulsemob services source:

```sh
$ git clone git://github.com/Infobase/pulsemob_webservices.git
$ pip install -r pulsemob_webservices/requirements.txt
```
### 3. Running the Harvest
1. Open pulsemob_webservices root folder;
2. Change configuration file name;

    ```sh
    $ mv pulsemob_webservices/harvest.cfg.default pulsemob_webservices/harvest.cfg
    ```
3. Adjust configuration parameters in *harvest.cfg*;
4. Create tables;

    ```sh
    $ python pulsemob_webservices/create_database_tables.py
    ```
5. Run.

    ```sh
    $ python pulsemob_webservices/harvest_job.py
    ```
It takes a lot of time to index articles for the first time.

### 4. Running the server
1. Activate virtualenv;

    ```sh
    $ source scielopulsemob-env/bin/activate
    ```
2. Open pulsemob_webservices root folder;
3. Change webservice configuration file name;

    ```sh
    $ mv pulsemob_webservices/webservices/settings.default.py pulsemob_webservices/webservices/settings.py
    ```

4. Adjust configuration parameters in settings.py. Make sure to set the SECRET_KEY to a large random value and keep it secret.

5. Create tables;

    ```sh
    $ python pulsemob_webservices/manage.py syncdb
    ```
6. Run.

    ```sh
    $ cd pulsemob_webservices/
    $ nohup gunicorn -b 0.0.0.0:8006 webservices.wsgi:application &
    ```
