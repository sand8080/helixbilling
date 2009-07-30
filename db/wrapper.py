import psycopg2
from conf.settings import DSN
from functools import partial

get_connection = partial(psycopg2.connect, DSN)

def fetchall_dicts(cursor):
    """
    Fetches all results and makes list of dicts with column names as keys
    """
    records = cursor.fetchall()
    columns = [info[0] for info in cursor.description]
    return [dict_from_lists(columns, rec) for rec in records]

def dict_from_lists(names, values):
    return dict(zip(names, values))

def transaction(get_conn=get_connection):
    def decorator(fun):
        def decorated(*args, **kwargs):
            conn = get_conn()
            kwargs['conn'] = conn
            try:
                result = fun(*args, **kwargs)
                conn.commit()
            except:
                conn.rollback()
                raise
            return result
        return decorated
    return decorator
