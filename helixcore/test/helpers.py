import psycopg2
from helixcore.db import wrapper
from functools import partial

DSN = 'dbname=sandbox host=localhost user=sandbox password=qazwsx'
get_connection = partial(psycopg2.connect, DSN)
transaction = partial(wrapper.transaction, get_connection)
