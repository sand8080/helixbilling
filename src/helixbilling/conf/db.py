import psycopg2
from eventlet import util
util.wrap_socket_with_coroutine_socket()

from functools import partial

import helixcore.db.wrapper as wrapper
from settings import DSN

get_connection = partial(psycopg2.connect, user=DSN['user'], database=DSN['database'], host=DSN['host'],
    password=DSN['password'])
transaction = partial(wrapper.transaction, get_connection)
