import psycopg2
from conf.settings import DSN
from functools import partial

get_connection = partial(psycopg2.connect, DSN)

def transaction(get_conn=get_connection):
    def do_transn(fun):
        def scoped_trans(*args, **kwargs):
            conn = get_conn()
            kwargs['conn'] = conn
            try:
                result = fun(*args, **kwargs)
                conn.commit()
            except:
                conn.rollback()
                raise
            return result
        return scoped_trans
    return do_transn
