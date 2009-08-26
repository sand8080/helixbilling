
def apply(curs):
    print 'Creating table chargeoff'
    curs.execute(
    '''
        CREATE TABLE chargeoff (
            id serial,
            client_id varchar NOT NULL,
            product_id varchar NOT NULL,
            locked_date timestamp with time zone NOT NULL,
            chargeoff_date timestamp with time zone NOT NULL DEFAULT now(),
            amount int,
            PRIMARY KEY(id)
        )
    ''')

    print 'Creating index chargeoff_client_id_product_id_idx on chargeoff'
    curs.execute(
    '''
        CREATE UNIQUE INDEX chargeoff_client_id_product_id_idx ON chargeoff(client_id, product_id);
    ''')

def revert(curs):
    print 'Dropping index chargeoff_client_id_product_id_idx on chargeoff'
    curs.execute('DROP INDEX chargeoff_client_id_product_id_idx')

    print 'Dropping table chargeoff'
    curs.execute('DROP TABLE chargeoff')

