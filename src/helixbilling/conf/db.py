import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

from eventlet.green import socket #@UnusedImport IGNORE:W0611
from functools import partial

import helixcore.db.wrapper as wrapper
from settings import DSN

get_connection = partial(psycopg2.connect, user=DSN['user'], database=DSN['database'], host=DSN['host'],
    password=DSN['password'])
transaction = partial(wrapper.transaction, get_connection)
