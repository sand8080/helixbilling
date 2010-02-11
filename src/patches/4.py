def apply(curs):
    print 'Creating table balance'
    curs.execute(
    '''
        CREATE TABLE balance (
            id serial,
            PRIMARY KEY(id),
            operator_id integer NOT NULL,
            FOREIGN KEY(operator_id) REFERENCES operator(id),
            active bool NOT NULL DEFAULT True,
            customer_id varchar NOT NULL,
            currency_id int NOT NULL,
            FOREIGN KEY(currency_id) REFERENCES currency(id),
            creation_date timestamp with time zone NOT NULL DEFAULT now(),
            available_real_amount NUMERIC DEFAULT 0,
            available_virtual_amount NUMERIC DEFAULT 0,
            locking_order varchar[] DEFAULT NULL,
            locked_amount NUMERIC DEFAULT 0,
            overdraft_limit NUMERIC DEFAULT 0
        )
    ''')

    print 'Creating unique index balance_customer_id_idx on balance'
    curs.execute(
    '''
        CREATE UNIQUE INDEX balance_customer_id_idx ON balance(customer_id)
    ''')

    print 'Creating index balance_operator_id_customer_id_idx on balance'
    curs.execute(
    '''
        CREATE INDEX balance_operator_id_customer_id_idx ON balance(operator_id, customer_id)
    ''')


def revert(curs):
    print 'Dropping index balance_operator_id_customer_id_idx on balance'
    curs.execute('DROP INDEX balance_operator_id_customer_id_idx')

    print 'Dropping unique index balance_customer_id_idx on balance'
    curs.execute('DROP INDEX balance_customer_id_idx')

    print 'Dropping table balance'
    curs.execute('DROP TABLE balance')

