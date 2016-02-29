bind = '127.0.0.1:8001'
backlog = 2048
workers = 3
errorlog = 'gunicorn-error.log'
accesslog = 'gunicorn-access.log'
loglevel = 'debug'
proc_name = 'gunicorn-my'
pidfile = '/var/run/my.pid'
