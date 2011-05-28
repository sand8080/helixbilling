def apply(curs):
    print 'Creating table transaction'
    curs.execute(
    '''
        CREATE TABLE transaction (
            id serial,
            PRIMARY KEY(id),
            environment_id integer NOT NULL,
            user_id integer NOT NULL,
            balance_id integer NOT NULL,
            FOREIGN KEY(balance_id) REFERENCES balance(id),
            real_amount DECIMAL,
            virtual_amount DECIMAL,
            creation_date timestamp with time zone NOT NULL DEFAULT now(),
            currency_code varchar NOT NULL,
            type varchar CHECK (type IN ('receipt', 'bonus', 'lock', 'chargeoff')),
            serialized_info varchar NOT NULL
        )
    ''')

    print 'Creating index transaction_environment_id_idx on transaction'
    curs.execute(
    '''
        CREATE INDEX transaction_environment_id_idx ON transaction(environment_id)
    ''')

    print 'Creating index transaction_user_id_idx on transaction'
    curs.execute(
    '''
        CREATE INDEX transaction_user_id_idx ON transaction(user_id)
    ''')

    print 'Creating index transaction_balance_id_idx on transaction'
    curs.execute(
    '''
        CREATE INDEX transaction_balance_id_idx ON transaction(balance_id)
    ''')

    print 'Creating index transaction_creation_date_idx on transaction'
    curs.execute(
    '''
        CREATE INDEX transaction_creation_date_idx ON transaction(creation_date)
    ''')


def revert(curs):
    print 'Dropping index transaction_environment_id_idx on balance'
    curs.execute('DROP INDEX IF EXISTS transaction_environment_id_idx')

    print 'Dropping index transaction_user_id_idx on balance'
    curs.execute('DROP INDEX IF EXISTS transaction_user_id_idx')

    print 'Dropping index transaction_balance_id_idx on balance'
    curs.execute('DROP INDEX IF EXISTS transaction_balance_id_idx')

    print 'Dropping index transaction_creation_date_idx on balance'
    curs.execute('DROP INDEX IF EXISTS transaction_creation_date_idx')

    print 'Dropping table transaction'
    curs.execute('DROP TABLE IF EXISTS transaction')

