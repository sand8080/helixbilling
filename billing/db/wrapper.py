import psycopg2
from functools import partial

from conf.settings import DSN
from utils import dict_from_lists

get_connection = partial(psycopg2.connect, DSN)

class EmptyResultSetError(Exception):
    pass

def fetchall_dicts(curs):
    """
    Fetches all results and makes list of dicts with column names as keys
    """
    records = curs.fetchall()
    columns = [info[0] for info in curs.description]
    return [dict_from_lists(columns, rec) for rec in records]

def fetchone_dict(curs):
    columns = [info[0] for info in curs.description]
    values = curs.fetchone()
    if values is None:
        raise EmptyResultSetError('Nothing to be fetched')
    return dict_from_lists(columns, values)

def transaction(get_conn=get_connection):
    def decorator(fun):
        def decorated(*args, **kwargs):
            conn = get_conn()
            curs = conn.cursor()
            kwargs['curs'] = curs
            try:
                result = fun(*args, **kwargs)
                curs.close()
                conn.commit()
                return result
            except:
                curs.close()
                conn.rollback()
                raise
        return decorated
    return decorator