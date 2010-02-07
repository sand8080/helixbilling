def apply(curs): #IGNORE:W0622
    print 'Creating table balance_lock'
    curs.execute(
    '''
        CREATE TABLE balance_lock (
            id serial,
            PRIMARY KEY(id),
            operator_id integer NOT NULL,
            FOREIGN KEY(operator_id) REFERENCES operator(id),
            customer_id varchar NOT NULL,
            product_id varchar NOT NULL,
            locking_date timestamp with time zone NOT NULL DEFAULT now(),
            real_amount int,
            virtual_amount int
        )
    ''')

    print 'Creating index balance_lock_operator_id_customer_id_idx on balance_lock'
    curs.execute(
    '''
        CREATE INDEX balance_lock_operator_id_customer_id_idx ON
            balance_lock(operator_id, customer_id)
    ''')

    print 'Creating unique index balance_lock_operator_id_customer_id_product_id_idx on balance_lock'
    curs.execute(
    '''
        CREATE INDEX balance_lock_operator_id_customer_id_product_id_idx ON
            balance_lock(operator_id, customer_id, product_id)
    ''')


def revert(curs):
    print 'Dropping index balance_lock_operator_id_customer_id_idx on balance_lock'
    curs.execute('DROP INDEX balance_lock_operator_id_customer_id_idx')

    print 'Dropping index balance_lock_operator_id_customer_id_product_id_idx on balance_lock'
    curs.execute('DROP INDEX balance_lock_operator_id_customer_id_product_id_idx')

    print 'Dropping table balance_lock'
    curs.execute('DROP TABLE balance_lock')

