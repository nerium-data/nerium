import os


workers = 3
worker_class = 'gevent'
timeout = 120
bind = '0.0.0.0:8081'
errorlog = '-'
accesslog = '-'
loglevel = os.getenv('LOGLEVEL', 'info')
