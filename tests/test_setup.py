import os

os.environ['DATABASE_URL'] = 'sqlite:///'
os.environ['QUERY_PATH'] = 'tests/query/'

query_name = 'basic'
sum_query_name = 'sum'
jinja_query_name = 'jinja'
