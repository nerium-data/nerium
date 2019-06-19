import os


workers = os.getenv("WORKERS", 3)
worker_class = "gevent"
timeout = 120
bind = "0.0.0.0:5000"
errorlog = "-"
accesslog = "-"
loglevel = os.getenv("LOGLEVEL", "info")
