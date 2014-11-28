========================================================
How to install a SciELO Pulsemob Webservices
========================================================

Install pre-requisites
----------------------

Before installing the SciELO Webservices, install the software listed below.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Server software

 +----------------+--------------------------------------------------------------+
 |**software**    |**product URL / installation instructions (for CentOS)**      |
 +================+==============================================================+
 | Python 2.7     | http://www.python.org/                                       |
 +----------------+--------------------------------------------------------------+
 | PostgreSQL     | http://www.postgresql.org/                                   |
 |                | Installation: yum install postgresql                         |
 +----------------|--------------------------------------------------------------+
 | PostgreSQL Dev | http://www.postgresql.org/                                   |
 |                | Installation: yum install postgresql-devel                   |
 +----------------+--------------------------------------------------------------+
 | GIT            | http://git-scm.com/                                          |
 |                | Installation: yum install git-core                           |
 +----------------+--------------------------------------------------------------+
 | Solr           | https://lucene.apache.org/solr/                              |
 |                | Installation: See https://github.com/Infobase/pulsemob_solr  | 
 +----------------+--------------------------------------------------------------+
 
1. Install each package below using the recommended installation method.

Note: Python comes pre-installed in most Linux distributions. If Python 2.7 is already installed, there is no need to install a newer version.

System-wide Python libraries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 +---------------+-------------------------------------------+------------------------+
 |**software**   |**product URL**                            |**installation method** |
 +===============+===========================================+========================+
 | pip           | http://pypi.python.org/pypi/pip           | sudo easy_install pip  | 
 +---------------+-------------------------------------------+------------------------+
 | virtualenv    | http://pypi.python.org/pypi/virtualenv    | sudo pip virtualenv    |
 +---------------+-------------------------------------------+------------------------+

 
Install the application environment
-----------------------------------

**Note: all of the remainig steps can be performed by a regular user without root access.**

2. Use virtualenv to create an application environment and activate it:

    $ virtualenv --distribute --no-site-packages -p python2.7 scielopulsemob-env
    $ source scielopulsemob-env/bin/activate
    (scielopulsemob-env)$   # note that the shell prompt displays the active virtual environment



Install the scielopulsemob services
-----------------------------------

3. Go to a suitable installation directory, download and install xylose library and checkout the scielopulsemob services source.

	(scielobooks-env)$ git clone https://github.com/scieloorg/xylose.git
	(scielobooks-env)$ cd xylose
	(scielobooks-env)$ python setup.py install
	(scielobooks-env)$ cd ..
    (scielopulsemob-env)$ git clone git://github.com/Infobase/pulsemob_webservices.git

4. With the `scielopulsemob-env` environment active, use `pip` to download and install the dependencies.

    (scielobooks-env)$ pip install -r pulsemob_webservices/requirements.txt

	

Configure the Database and Solr
-------------------------------

5. Create a new database instance in Postgres.

6. Create a new colletion in Solr.

7. Change the configuration files below accordingly database and solr instances:

	pulsemob_webservices/pulsemob_webservices/harvest.cfg
	pulsemob_webservices/pulsemob_webservices/tests/harvest_test.cfg

8. Create the database tables:

	(scielobooks-env)$ cd pulsemob_webservices/pulsemob_webservices
    (scielobooks-env)$ python -u create_database_tables.py


Test and run the harvest script
-------------------------------
	
9. Run automated tests:

	(scielobooks-env)$ cd pulsemob_webservices/pulsemob_webservices
    (scielobooks-env)$ python -u run_tests.py

	
10. Run the harvest script to collect article data:
	(scielobooks-env)$ cd pulsemob_webservices/pulsemob_webservices
	
# without nohup:
	(scielobooks-env)$ python -u harvest_job.py
	
# with nohup:
	(scielobooks-env)$ nohup python -u harvest_job.py &
	(scielobooks-env)$ tail -f nohup.out
