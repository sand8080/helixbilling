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
            order_id varchar NOT NULL,
            order_type varchar,
            locking_date timestamp with time zone NOT NULL DEFAULT now(),
            real_amount NUMERIC,
            virtual_amount NUMERIC
        )
    ''')

    print 'Creating index balance_lock_operator_id_customer_id_idx on balance_lock'
    curs.execute(
    '''
        CREATE INDEX balance_lock_operator_id_customer_id_idx ON
            balance_lock(operator_id, customer_id)
    ''')

    print 'Creating unique index balance_lock_operator_id_customer_id_order_id_idx on balance_lock'
    curs.execute(
    '''
        CREATE UNIQUE INDEX balance_lock_operator_id_customer_id_order_id_idx ON
            balance_lock(operator_id, customer_id, order_id)
    ''')

    print 'Creating index balance_lock_operator_id_customer_id_order_type_idx on balance_lock'
    curs.execute(
    '''
        CREATE INDEX balance_lock_operator_id_customer_id_order_type_idx ON
            balance_lock(operator_id, customer_id, order_type)
    ''')


def revert(curs):
    print 'Dropping index balance_lock_operator_id_customer_id_order_type_idx on balance_lock'
    curs.execute('DROP INDEX balance_lock_operator_id_customer_id_order_type_idx')

    print 'Dropping unique index balance_lock_operator_id_customer_id_order_id_idx on balance_lock'
    curs.execute('DROP INDEX balance_lock_operator_id_customer_id_order_id_idx')

    print 'Dropping index balance_lock_operator_id_customer_id_idx on balance_lock'
    curs.execute('DROP INDEX balance_lock_operator_id_customer_id_idx')

    print 'Dropping table balance_lock'
    curs.execute('DROP TABLE balance_lock')

