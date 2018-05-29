import os

os.environ['DATABASE_URL'] = 'sqlite:///'
os.environ['QUERY_PATH'] = 'tests/query/'
os.environ['CONFIG_PATH'] = 'tests/test-config.yaml'

query_name = 'basic'
sum_query_name = 'sum'
jinja_query_name = 'jinja'
