
def apply(curs):
    print 'Creating table balance_lock'
    curs.execute(
    '''
        CREATE TABLE balance_lock (
            id serial,
            client_id varchar NOT NULL,
            product_id varchar NOT NULL,
            locked_date timestamp with time zone NOT NULL DEFAULT now(),
            amount int,
            PRIMARY KEY(id)
        )
    ''')

    print 'Creating index balance_lock_client_id_product_id_idx on balance_lock'
    curs.execute(
    '''
        CREATE UNIQUE INDEX balance_lock_client_id_product_id_idx ON balance_lock(client_id, product_id);
    ''')

def revert(curs):
    print 'Dropping index balance_lock_client_id_product_id_idx on balance_lock'
    curs.execute('DROP INDEX balance_lock_client_id_product_id_idx')

    print 'Dropping table balance_lock'
    curs.execute('DROP TABLE balance_lock')

