def apply(curs):
    print 'Creating table balance_lock'
    curs.execute(
    '''
        CREATE TABLE balance_lock (
            id serial,
            PRIMARY KEY(id),
            environment_id integer NOT NULL,
            user_id int NOT NULL,
            balance_id integer NOT NULL,
            FOREIGN KEY(balance_id) REFERENCES balance(id),
            currency_id integer NOT NULL,
            FOREIGN KEY(currency_id) REFERENCES currency(id),
            real_amount DECIMAL,
            virtual_amount DECIMAL,
            order_id varchar,
            locking_order varchar[] NOT NULL,
            creation_date timestamp with time zone NOT NULL DEFAULT now(),
            serialized_info varchar NOT NULL
        )
    ''')

    print 'Creating index balance_lock_environment_id_idx on balance_lock'
    curs.execute(
    '''
        CREATE INDEX balance_lock_environment_id_idx ON balance_lock(environment_id)
    ''')

    print 'Creating index balance_lock_user_id_idx on balance_lock'
    curs.execute(
    '''
        CREATE INDEX balance_lock_user_id_idx ON balance_lock(user_id)
    ''')

    print 'Creating index balance_lock_currency_id_idx on balance_lock'
    curs.execute(
    '''
        CREATE INDEX balance_lock_currency_id_idx ON balance_lock(currency_id)
    ''')

    print 'Creating index balance_lock_balance_id_idx on balance_lock'
    curs.execute(
    '''
        CREATE INDEX balance_lock_balance_id_idx ON balance_lock(balance_id)
    ''')

    print 'Creating index balance_lock_creation_date_idx on balance_lock'
    curs.execute(
    '''
        CREATE INDEX balance_lock_creation_date_idx ON balance_lock(creation_date)
    ''')

    print 'Creating index balance_lock_order_id_idx on balance_lock'
    curs.execute(
    '''
        CREATE INDEX balance_lock_order_id_idx ON balance_lock(order_id)
    ''')


def revert(curs):
    print 'Dropping index balance_lock_order_id_idx on balance_lock'
    curs.execute('DROP INDEX IF EXISTS balance_lock_order_id_idx')

    print 'Dropping index balance_lock_creation_date_idx on balance_lock'
    curs.execute('DROP INDEX IF EXISTS balance_lock_creation_date_idx')

    print 'Dropping index transaction_user_id_idx on balance_lock'
    curs.execute('DROP INDEX IF EXISTS transaction_user_id_idx')

    print 'Dropping index transaction_balance_id_idx on balance_lock'
    curs.execute('DROP INDEX IF EXISTS transaction_balance_id_idx')

    print 'Dropping index transaction_currency_id_idx on balance_lock'
    curs.execute('DROP INDEX IF EXISTS transaction_currency_id_idx')

    print 'Dropping index transaction_creation_date_idx on balance_lock'
    curs.execute('DROP INDEX IF EXISTS transaction_creation_date_idx')

    print 'Dropping table balance_lock'
    curs.execute('DROP TABLE IF EXISTS balance_lock')

